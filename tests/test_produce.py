import json
import shutil
import subprocess

import pytest

from pipeline.produce import (
    Moment,
    assemble_compilation,
    build_concat_list,
    build_cut_command,
    cut_clip,
    load_job,
    loudness_filter,
    moment_from_dict,
    order_for_compilation,
    parse_srt,
    parse_timestamp,
    produce_compilation,
    shift_srt,
    subtitles_filter,
    vertical_filter,
)

FFMPEG = shutil.which("ffmpeg")
FFPROBE = shutil.which("ffprobe")
needs_ffmpeg = pytest.mark.skipif(
    FFMPEG is None or FFPROBE is None, reason="ffmpeg/ffprobe not installed"
)


# ─── timestamps & moments ────────────────────────────────────────────────

def test_parse_timestamp_seconds_and_clock_forms():
    assert parse_timestamp(83.5) == 83.5
    assert parse_timestamp("90") == 90.0
    assert parse_timestamp("01:30") == 90.0
    assert parse_timestamp("01:02:03.5") == 3723.5


def test_moment_from_dict_accepts_both_key_styles():
    a = moment_from_dict({"title": "A", "start": "00:10", "end": "00:40", "score": 9})
    b = moment_from_dict({"title": "B", "start_s": 10, "end_s": 40})
    assert (a.start_s, a.end_s, a.score, a.duration_s) == (10.0, 40.0, 9, 30.0)
    assert (b.start_s, b.end_s) == (10.0, 40.0)


def test_moment_rejects_end_before_start():
    with pytest.raises(ValueError):
        moment_from_dict({"title": "bad", "start": 50, "end": 40})


# ─── filters & command building (pure) ───────────────────────────────────

def test_blurpad_graph_scales_blurs_and_overlays():
    graph = vertical_filter("blurpad", 1080, 1920)
    assert "boxblur" in graph
    assert "overlay" in graph
    assert graph.endswith("[vout]")


def test_crop_graph_fills_and_crops():
    graph = vertical_filter("crop", 720, 1280)
    assert "scale=720:1280" in graph
    assert "crop=720:1280" in graph


def test_vertical_filter_rejects_unknown_mode():
    with pytest.raises(ValueError):
        vertical_filter("stretch")


def test_loudness_modes():
    assert loudness_filter("keep") is None
    assert "loudnorm" in loudness_filter("safe")
    with pytest.raises(ValueError):
        loudness_filter("blast")


def test_build_cut_command_is_frame_accurate_reencode():
    cmd = build_cut_command("src.mp4", 10, 40, "out.mp4", vertical="crop",
                            width=720, height=1280, loudness="safe")
    assert cmd[:2] == ["ffmpeg", "-y"]
    assert cmd[cmd.index("-ss") + 1] == "10.000"
    assert cmd[cmd.index("-t") + 1] == "30.000"
    assert "-filter_complex" in cmd
    assert "libx264" in cmd
    assert "loudnorm" in cmd[cmd.index("-af") + 1]
    assert cmd[-1] == "out.mp4"


def test_build_cut_command_without_vertical_has_no_filter_graph():
    cmd = build_cut_command("src.mp4", 0, 5, "out.mp4")
    assert "-filter_complex" not in cmd
    assert "-af" not in cmd


# ─── subtitles ───────────────────────────────────────────────────────────

SRT = """1
00:00:05,000 --> 00:00:08,000
Too early

2
00:01:10,000 --> 00:01:14,500
The moment itself

3
00:01:14,000 --> 00:01:20,000
Straddles the end
"""


def test_parse_srt_reads_entries():
    entries = parse_srt(SRT)
    assert len(entries) == 3
    assert entries[1] == (70.0, 74.5, "The moment itself")


def test_shift_srt_extracts_and_retimes_the_clip_window():
    shifted = shift_srt(SRT, offset_s=60, duration_s=18)
    entries = parse_srt(shifted)
    assert [text for _, _, text in entries] == ["The moment itself", "Straddles the end"]
    assert entries[0][:2] == (10.0, 14.5)
    assert entries[1][:2] == (14.0, 18.0)  # end clamped to the clip length


def test_shift_srt_drops_everything_outside_the_window():
    assert shift_srt(SRT, offset_s=300, duration_s=10) == ""


def test_subtitles_filter_escapes_windows_style_paths():
    assert subtitles_filter("captions.srt") == "subtitles=filename='captions.srt'"
    assert "\\:" in subtitles_filter("C:\\clips\\cap.srt")


# ─── compilation ordering & concat ───────────────────────────────────────

def test_compilation_order_puts_best_clip_last():
    moments = [
        Moment("mid", 0, 10, score=9),
        Moment("best", 20, 30, score=10),
        Moment("weakest winner", 40, 50, score=8),
    ]
    ordered = order_for_compilation(moments)
    assert [m.title for m in ordered] == ["weakest winner", "mid", "best"]


def test_compilation_order_keeps_unscored_at_the_front():
    moments = [Moment("scored", 0, 10, score=8), Moment("unscored", 20, 30)]
    ordered = order_for_compilation(moments)
    assert [m.title for m in ordered] == ["unscored", "scored"]


def test_concat_list_escapes_quotes(tmp_path):
    list_file = build_concat_list(["a'b.mp4", "plain.mp4"], tmp_path / "list.txt")
    lines = list_file.read_text(encoding="utf-8").splitlines()
    assert lines[0].endswith("a'\\''b.mp4'")
    assert lines[1].endswith("plain.mp4'")


# ─── job loading ─────────────────────────────────────────────────────────

def test_load_job_resolves_paths_against_the_job_folder(tmp_path):
    (tmp_path / "job.json").write_text(json.dumps({
        "source": "footage/src.mp4",
        "output_dir": "out",
        "format": "vertical",
        "moments": [{"title": "One", "start": "00:05", "end": "00:15", "score": 9}],
        "compilation": {"enabled": True, "name": "long.mp4"},
    }), encoding="utf-8")
    job = load_job(tmp_path / "job.json")
    assert job.source == str(tmp_path / "footage" / "src.mp4")
    assert job.output_dir == str(tmp_path / "out")
    assert job.compilation_enabled is True
    assert job.compilation_name == "long.mp4"
    assert job.moments[0].start_s == 5.0


def test_load_job_rejects_an_empty_moment_list(tmp_path):
    (tmp_path / "job.json").write_text(
        json.dumps({"source": "s.mp4", "moments": []}), encoding="utf-8")
    with pytest.raises(ValueError):
        load_job(tmp_path / "job.json")


# ─── integration: real ffmpeg, tiny synthetic source ─────────────────────

def _make_source(path, seconds=6):
    subprocess.run(
        ["ffmpeg", "-y",
         "-f", "lavfi", "-i", f"testsrc2=size=320x180:rate=30:duration={seconds}",
         "-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
         str(path)],
        check=True, capture_output=True,
    )


def _probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", "-show_streams", str(path)],
        check=True, capture_output=True, text=True,
    )
    return json.loads(out.stdout)


@needs_ffmpeg
def test_cut_clip_produces_a_vertical_blurpad_short(tmp_path):
    source = tmp_path / "src.mp4"
    _make_source(source)
    out = cut_clip(source, 1, 3, tmp_path / "short.mp4",
                   vertical="blurpad", width=360, height=640)
    info = _probe(out)
    video = next(s for s in info["streams"] if s["codec_type"] == "video")
    assert (video["width"], video["height"]) == (360, 640)
    assert abs(float(info["format"]["duration"]) - 2.0) < 0.35


@needs_ffmpeg
def test_cut_clip_burns_captions_from_a_source_timed_srt(tmp_path):
    source = tmp_path / "src.mp4"
    _make_source(source)
    srt = tmp_path / "source.srt"
    srt.write_text(
        "1\n00:00:01,500 --> 00:00:02,500\nCaption inside the clip\n",
        encoding="utf-8",
    )
    out = cut_clip(source, 1, 3, tmp_path / "captioned.mp4",
                   captions_srt=srt, captions_from_source=True)
    assert out.exists() and out.stat().st_size > 0


@needs_ffmpeg
def test_produce_compilation_joins_clips_best_last(tmp_path):
    source = tmp_path / "src.mp4"
    _make_source(source, seconds=9)
    job_file = tmp_path / "job.json"
    job_file.write_text(json.dumps({
        "source": "src.mp4",
        "output_dir": "out",
        "format": "original",
        "moments": [
            {"title": "Best", "start": 6, "end": 8, "score": 10},
            {"title": "Opener", "start": 0, "end": 2, "score": 8},
        ],
        "compilation": {"enabled": True, "name": "long.mp4"},
    }), encoding="utf-8")
    out = produce_compilation(load_job(job_file))
    info = _probe(out)
    assert abs(float(info["format"]["duration"]) - 4.0) < 0.5


@needs_ffmpeg
def test_assemble_compilation_rejects_no_clips(tmp_path):
    with pytest.raises(ValueError):
        assemble_compilation([], tmp_path / "none.mp4")
