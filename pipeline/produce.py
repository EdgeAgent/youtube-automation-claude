"""Produce — actually MAKE the videos: cut, format, caption, assemble.

Selection (``pipeline/select.py``) decides *which* moments deserve to
exist. This module turns those decisions into finished video files,
working only on footage the user supplies locally:

- **Cut** each winning moment out of the source video at its
  timestamps (frame-accurate re-encode, never a stream copy guess).
- **Format** clips as vertical 9:16 Shorts — blurred-pad (the source
  scaled to fit over a blurred, zoomed copy of itself) or centre crop.
- **Caption** by burning subtitles from an SRT file. Captions can be
  supplied per clip, or as one SRT timed against the full source —
  in that case the relevant slice is extracted and re-timed here.
- **Assemble** compilations: the winning clips joined into one long
  video, ordered countdown-style with the best-scoring clip LAST
  (see docs/packaging-playbook.md).
- **Audio** is the source's own audio, kept as-is by default. The
  ``safe`` loudness mode runs a single-pass loudnorm toward YouTube's
  -14 LUFS neighbourhood so a quiet or hot source doesn't surprise
  you on upload. If you later add a narration track, duck the source
  under it (ffmpeg's ``sidechaincompress``) instead of just turning
  it down — the source should dip when the voice speaks, not sit
  under it the whole time.

Hard limits, by design: this module only reads files on your own
machine. It does not download, scrape, or rip footage from anywhere,
and it does not upload anything. Publishing stays a human step.

Everything runs through the ffmpeg CLI (stdlib ``subprocess`` only).

Job files are JSON::

    {
      "source": "footage/source.mp4",
      "output_dir": "out",
      "format": "vertical",            // or "original"
      "vertical_mode": "blurpad",      // or "crop"
      "loudness": "keep",              // or "safe"
      "captions": "footage/source.srt",  // optional, timed to the source
      "moments": [
        {"title": "The Escape", "start": "01:12", "end": "01:40", "score": 9},
        {"title": "The Chase", "start": 240.0, "end": 268.5, "score": 10}
      ],
      "compilation": {"enabled": true, "name": "compilation.mp4"}
    }

Paths inside a job file are resolved relative to the job file itself.
Timestamps accept seconds (``83.5``) or clock strings (``"01:23"``,
``"01:02:03.5"``). A moment's ``score`` is the winner picker's /10 —
it drives compilation order (best last). A moment may also carry its
own ``source`` and its own clip-aligned ``captions`` file.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

SHORT_W, SHORT_H = 1080, 1920  # vertical 9:16 master size for Shorts
VERTICAL_MODES = ("blurpad", "crop")
LOUDNESS_MODES = ("keep", "safe")
# Single-pass EBU R128 loudnorm aimed at YouTube's ~-14 LUFS playback
# normalisation. Two-pass loudnorm is more precise; this is the safe
# one-knob version and it never touches the audio in "keep" mode.
SAFE_LOUDNORM = "loudnorm=I=-14:TP=-1.5:LRA=11"


# ─── timestamps ──────────────────────────────────────────────────────────

def parse_timestamp(value) -> float:
    """Parse seconds (number or numeric string) or MM:SS / HH:MM:SS."""
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        raise ValueError("Empty timestamp")
    if ":" not in text:
        return float(text)
    parts = text.split(":")
    if len(parts) not in (2, 3):
        raise ValueError(f"Unsupported timestamp: {value!r}")
    numbers = [float(p) for p in parts]
    if len(numbers) == 2:
        minutes, seconds = numbers
        return minutes * 60 + seconds
    hours, minutes, seconds = numbers
    return hours * 3600 + minutes * 60 + seconds


# ─── moments and jobs ────────────────────────────────────────────────────

@dataclass
class Moment:
    """One selected moment to cut. Mirrors the winner picker's output."""

    title: str
    start_s: float
    end_s: float
    score: float | None = None
    source: str | None = None    # per-moment source override
    captions: str | None = None  # per-moment, clip-aligned SRT

    @property
    def duration_s(self) -> float:
        return self.end_s - self.start_s

    def validate(self) -> None:
        if self.end_s <= self.start_s:
            raise ValueError(
                f"Moment {self.title!r}: end ({self.end_s}) must be after start ({self.start_s})"
            )


def moment_from_dict(data: dict) -> Moment:
    """Build a Moment from a job-file dict (start/end or start_s/end_s)."""
    start = data.get("start_s", data.get("start"))
    end = data.get("end_s", data.get("end"))
    if start is None or end is None:
        raise ValueError(f"Moment is missing start/end: {data!r}")
    moment = Moment(
        title=str(data.get("title", "untitled")),
        start_s=parse_timestamp(start),
        end_s=parse_timestamp(end),
        score=data.get("score"),
        source=data.get("source"),
        captions=data.get("captions"),
    )
    moment.validate()
    return moment


@dataclass
class ProduceJob:
    source: str
    moments: list
    output_dir: str = "out"
    format: str = "vertical"          # "vertical" (9:16 Shorts) or "original"
    vertical_mode: str = "blurpad"    # "blurpad" or "crop"
    loudness: str = "keep"            # "keep" or "safe"
    captions: str | None = None       # one SRT timed against the full source
    width: int = SHORT_W
    height: int = SHORT_H
    compilation_enabled: bool = False
    compilation_name: str = "compilation.mp4"

    def validate(self) -> None:
        if self.format not in ("vertical", "original"):
            raise ValueError(f"Unknown format: {self.format!r}")
        if self.vertical_mode not in VERTICAL_MODES:
            raise ValueError(f"Unknown vertical_mode: {self.vertical_mode!r}")
        if self.loudness not in LOUDNESS_MODES:
            raise ValueError(f"Unknown loudness: {self.loudness!r}")
        if not self.moments:
            raise ValueError("A produce job needs at least one moment")
        for moment in self.moments:
            moment.validate()


def load_job(path: str | Path) -> ProduceJob:
    """Load a JSON job file; relative paths resolve against its folder."""
    job_path = Path(path)
    data = json.loads(job_path.read_text(encoding="utf-8"))
    base = job_path.parent

    def resolve(value):
        if value is None:
            return None
        p = Path(value)
        return str(p if p.is_absolute() else base / p)

    moments = []
    for raw in data.get("moments", []):
        moment = moment_from_dict(raw)
        moment.source = resolve(moment.source)
        moment.captions = resolve(moment.captions)
        moments.append(moment)

    compilation = data.get("compilation") or {}
    job = ProduceJob(
        source=resolve(data["source"]),
        moments=moments,
        output_dir=resolve(data.get("output_dir", "out")),
        format=data.get("format", "vertical"),
        vertical_mode=data.get("vertical_mode", "blurpad"),
        loudness=data.get("loudness", "keep"),
        captions=resolve(data.get("captions")),
        width=int(data.get("width", SHORT_W)),
        height=int(data.get("height", SHORT_H)),
        compilation_enabled=bool(compilation.get("enabled", False)),
        compilation_name=str(compilation.get("name", "compilation.mp4")),
    )
    job.validate()
    return job


# ─── filter builders (pure functions — the testable core) ────────────────

def vertical_filter(mode: str, width: int = SHORT_W, height: int = SHORT_H) -> str:
    """Return the -filter_complex graph that makes a clip vertical 9:16.

    blurpad: source scaled to fit inside the frame, centred over a
    blurred, frame-filling zoom of itself — nothing is cropped away.
    crop: source scaled to fill the frame and centre-cropped — the
    sides are lost, but the subject fills the screen.
    """
    if mode == "blurpad":
        return (
            f"split[a][b];"
            f"[a]scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},boxblur=20:5[bg];"
            f"[b]scale={width}:{height}:force_original_aspect_ratio=decrease[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2[vout]"
        )
    if mode == "crop":
        return (
            f"scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},setsar=1[vout]"
        )
    raise ValueError(f"Unknown vertical mode: {mode!r}")


def loudness_filter(mode: str) -> str | None:
    """Audio filter for a loudness mode, or None to keep source audio."""
    if mode == "keep":
        return None
    if mode == "safe":
        return SAFE_LOUDNORM
    raise ValueError(f"Unknown loudness mode: {mode!r}")


def build_cut_command(source, start_s: float, end_s: float, out_path, *,
                      vertical: str | None = None,
                      width: int = SHORT_W, height: int = SHORT_H,
                      loudness: str = "keep") -> list:
    """Build the ffmpeg argv that cuts one clip. Pure — runs nothing.

    Re-encodes (libx264/aac) so the cut is frame-accurate; a stream
    copy can only cut on keyframes and will drift by seconds.
    """
    duration = end_s - start_s
    if duration <= 0:
        raise ValueError(f"Clip end ({end_s}) must be after start ({start_s})")
    cmd = ["ffmpeg", "-y", "-ss", f"{start_s:.3f}", "-i", str(source),
           "-t", f"{duration:.3f}"]
    if vertical:
        cmd += ["-filter_complex", vertical_filter(vertical, width, height),
                "-map", "[vout]", "-map", "0:a?"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "18"]
    audio = loudness_filter(loudness)
    if audio:
        cmd += ["-af", audio]
    cmd += ["-c:a", "aac", "-b:a", "160k", str(out_path)]
    return cmd


# ─── subtitles ───────────────────────────────────────────────────────────

_SRT_TIME_RE = re.compile(
    r"(\d+):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d+):(\d{2}):(\d{2})[,.](\d{3})"
)


def _srt_stamp_to_s(hours, minutes, seconds, millis) -> float:
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(millis) / 1000


def _s_to_srt_stamp(total_s: float) -> str:
    total_s = max(0.0, total_s)
    millis = int(round((total_s - int(total_s)) * 1000))
    whole = int(total_s)
    if millis == 1000:  # rounding carried into the next second
        whole += 1
        millis = 0
    hours, rem = divmod(whole, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def parse_srt(text: str) -> list:
    """Parse SRT text into [(start_s, end_s, text), ...]."""
    entries = []
    for block in re.split(r"\r?\n\s*\r?\n", text.strip()):
        lines = [line for line in block.strip().splitlines() if line.strip()]
        if not lines:
            continue
        timing_at = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if timing_at is None:
            continue
        match = _SRT_TIME_RE.search(lines[timing_at])
        if not match:
            continue
        start = _srt_stamp_to_s(*match.groups()[:4])
        end = _srt_stamp_to_s(*match.groups()[4:])
        body = "\n".join(lines[timing_at + 1:])
        if body:
            entries.append((start, end, body))
    return entries


def shift_srt(text: str, offset_s: float, duration_s: float | None = None) -> str:
    """Re-time a source-timed SRT onto a clip that starts at offset_s.

    Entries outside the clip window are dropped; entries straddling
    the edges are clamped. Output is renumbered from 1.
    """
    window_end = None if duration_s is None else offset_s + duration_s
    kept = []
    for start, end, body in parse_srt(text):
        if end <= offset_s:
            continue
        if window_end is not None and start >= window_end:
            continue
        new_start = max(0.0, start - offset_s)
        new_end = end - offset_s
        if window_end is not None:
            new_end = min(new_end, duration_s)
        if new_end <= new_start:
            continue
        kept.append((new_start, new_end, body))
    blocks = [
        f"{i}\n{_s_to_srt_stamp(s)} --> {_s_to_srt_stamp(e)}\n{body}"
        for i, (s, e, body) in enumerate(kept, start=1)
    ]
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def _escape_filter_path(path) -> str:
    """Escape a filesystem path for use inside an ffmpeg filter arg."""
    text = str(path).replace("\\", "/")
    return text.replace(":", "\\:").replace("'", "\\'")


def subtitles_filter(srt_path) -> str:
    """The -vf chain that burns an SRT into the picture."""
    return f"subtitles=filename='{_escape_filter_path(srt_path)}'"


# ─── ffmpeg runners ──────────────────────────────────────────────────────

def find_ffmpeg() -> str:
    """Locate the ffmpeg binary or raise a plain-language error."""
    exe = shutil.which("ffmpeg")
    if exe is None:
        raise RuntimeError(
            "ffmpeg not found on PATH. Install it (see setup.sh / INSTALL.md) "
            "— the produce stage shells out to it."
        )
    return exe


def _run(cmd: list) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = "\n".join(proc.stderr.splitlines()[-15:])
        raise RuntimeError(f"ffmpeg failed ({' '.join(cmd[:2])} ...):\n{tail}")


def cut_clip(source, start_s: float, end_s: float, out_path, *,
             vertical: str | None = None,
             width: int = SHORT_W, height: int = SHORT_H,
             captions_srt: str | Path | None = None,
             captions_from_source: bool = False,
             loudness: str = "keep") -> Path:
    """Cut one clip, optionally vertical-formatted and captioned.

    ``captions_srt`` is an SRT for this clip. If ``captions_from_source``
    is true, the SRT is timed against the full source and the matching
    slice is extracted and re-timed automatically; otherwise it must
    already be timed against the clip itself.
    """
    ffmpeg = find_ffmpeg()
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    duration = end_s - start_s

    with tempfile.TemporaryDirectory(prefix="produce-") as tmp:
        tmp = Path(tmp)
        stage = out if captions_srt is None else tmp / "uncaptioned.mp4"
        cmd = build_cut_command(source, start_s, end_s, stage, vertical=vertical,
                                width=width, height=height, loudness=loudness)
        cmd[0] = ffmpeg
        _run(cmd)
        if captions_srt is None:
            return out

        srt_path = Path(captions_srt)
        if captions_from_source:
            shifted = tmp / "clip.srt"
            shifted.write_text(
                shift_srt(srt_path.read_text(encoding="utf-8"), start_s, duration),
                encoding="utf-8",
            )
            srt_path = shifted
        burn = [ffmpeg, "-y", "-i", str(stage),
                "-vf", subtitles_filter(srt_path),
                "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                "-c:a", "copy", str(out)]
        _run(burn)
    return out


# ─── compilations ────────────────────────────────────────────────────────

def order_for_compilation(moments: list) -> list:
    """Order moments countdown-style: weakest winner first, best LAST.

    Moments without a score keep their relative order at the front —
    unscored never outranks scored, and the highest score closes.
    """
    return sorted(
        moments,
        key=lambda m: (m.score is not None, m.score if m.score is not None else 0.0),
    )


def build_concat_list(clip_paths: list, list_path) -> Path:
    """Write an ffmpeg concat-demuxer list file for the given clips."""
    lines = []
    for clip in clip_paths:
        absolute = str(Path(clip).resolve())
        lines.append("file '" + absolute.replace("'", "'\\''") + "'")
    out = Path(list_path)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def assemble_compilation(clip_paths: list, out_path, *, loudness: str = "keep") -> Path:
    """Join already-cut clips (same format) into one long video."""
    if not clip_paths:
        raise ValueError("A compilation needs at least one clip")
    ffmpeg = find_ffmpeg()
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="produce-concat-") as tmp:
        list_file = build_concat_list(clip_paths, Path(tmp) / "clips.txt")
        cmd = [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
               "-c:v", "libx264", "-preset", "medium", "-crf", "18"]
        audio = loudness_filter(loudness)
        if audio:
            cmd += ["-af", audio]
        cmd += ["-c:a", "aac", "-b:a", "160k", str(out)]
        _run(cmd)
    return out


# ─── job orchestration ───────────────────────────────────────────────────

@dataclass
class ClipResult:
    title: str
    out_path: str
    start_s: float
    end_s: float
    score: float | None = None


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "clip"


def _cut_moment(job: ProduceJob, moment: Moment, out_path: Path, *,
                vertical: str | None) -> ClipResult:
    captions = moment.captions
    from_source = False
    if captions is None and job.captions is not None:
        captions, from_source = job.captions, True
    cut_clip(
        moment.source or job.source, moment.start_s, moment.end_s, out_path,
        vertical=vertical, width=job.width, height=job.height,
        captions_srt=captions, captions_from_source=from_source,
        loudness=job.loudness,
    )
    return ClipResult(title=moment.title, out_path=str(out_path),
                      start_s=moment.start_s, end_s=moment.end_s,
                      score=moment.score)


def produce_shorts(job: ProduceJob) -> list:
    """Cut every moment in the job into its own finished Short."""
    out_dir = Path(job.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    vertical = job.vertical_mode if job.format == "vertical" else None
    results = []
    for i, moment in enumerate(job.moments, start=1):
        out_path = out_dir / f"{i:02d}-{_slugify(moment.title)}.mp4"
        results.append(_cut_moment(job, moment, out_path, vertical=vertical))
    return results


def produce_compilation(job: ProduceJob, out_path=None) -> Path:
    """Cut the job's moments and assemble them, best clip last."""
    out_dir = Path(job.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    vertical = job.vertical_mode if job.format == "vertical" else None
    with tempfile.TemporaryDirectory(prefix="produce-parts-") as tmp:
        parts = []
        for i, moment in enumerate(order_for_compilation(job.moments), start=1):
            part = Path(tmp) / f"{i:02d}-{_slugify(moment.title)}.mp4"
            _cut_moment(job, moment, part, vertical=vertical)
            parts.append(part)
        target = Path(out_path) if out_path else out_dir / job.compilation_name
        return assemble_compilation(parts, target, loudness=job.loudness)


# ─── CLI ─────────────────────────────────────────────────────────────────

def _add_common_cut_args(parser) -> None:
    parser.add_argument("--vertical", choices=["none", *VERTICAL_MODES], default="none")
    parser.add_argument("--width", type=int, default=SHORT_W)
    parser.add_argument("--height", type=int, default=SHORT_H)
    parser.add_argument("--loudness", choices=list(LOUDNESS_MODES), default="keep")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="produce",
        description="Make the videos: cut winning moments out of footage you "
                    "supply locally, format Shorts, burn captions, assemble "
                    "compilations. Nothing is downloaded; nothing is uploaded.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_cut = sub.add_parser("cut", help="Cut one clip from a source video")
    p_cut.add_argument("source")
    p_cut.add_argument("--start", required=True, help="seconds or MM:SS / HH:MM:SS")
    p_cut.add_argument("--end", required=True, help="seconds or MM:SS / HH:MM:SS")
    p_cut.add_argument("--out", required=True)
    p_cut.add_argument("--captions", help="SRT file to burn in")
    p_cut.add_argument("--captions-from-source", action="store_true",
                       help="the SRT is timed against the full source, not the clip")
    _add_common_cut_args(p_cut)

    p_shorts = sub.add_parser("shorts", help="Cut every moment in a job file into a Short")
    p_shorts.add_argument("job")

    p_comp = sub.add_parser("compilation", help="Assemble a job's moments into one long video, best last")
    p_comp.add_argument("job")
    p_comp.add_argument("--out", help="override the compilation output path")

    p_shift = sub.add_parser("shift-captions", help="Extract/re-time the SRT slice for one clip")
    p_shift.add_argument("srt")
    p_shift.add_argument("--offset", required=True, help="clip start in the source")
    p_shift.add_argument("--duration", help="clip length in seconds (default: to the end)")
    p_shift.add_argument("--out", required=True)

    args = parser.parse_args(argv)
    try:
        if args.command == "cut":
            out = cut_clip(
                args.source, parse_timestamp(args.start), parse_timestamp(args.end),
                args.out,
                vertical=None if args.vertical == "none" else args.vertical,
                width=args.width, height=args.height,
                captions_srt=args.captions,
                captions_from_source=args.captions_from_source,
                loudness=args.loudness,
            )
            print(f"cut -> {out}")
        elif args.command == "shorts":
            job = load_job(args.job)
            for result in produce_shorts(job):
                print(f"short -> {result.out_path}")
        elif args.command == "compilation":
            job = load_job(args.job)
            out = produce_compilation(job, out_path=args.out)
            print(f"compilation -> {out}")
        elif args.command == "shift-captions":
            duration = None if args.duration is None else parse_timestamp(args.duration)
            shifted = shift_srt(
                Path(args.srt).read_text(encoding="utf-8"),
                parse_timestamp(args.offset), duration,
            )
            Path(args.out).write_text(shifted, encoding="utf-8")
            print(f"captions -> {args.out}")
    except (ValueError, RuntimeError, FileNotFoundError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
