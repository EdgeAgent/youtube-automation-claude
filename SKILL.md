---
name: youtube-automation
description: Run a niche-agnostic YouTube pipeline end to end — pick only winning moments, actually produce the videos (cut, vertical-format, caption, assemble compilations with ffmpeg on footage the user supplies locally), build the full SEO pack, make thumbnails from real frames, and gate everything through QC before a human publishes. Use when the user wants to start or run a YouTube channel in any niche with this repo, choose a niche, produce or package a video, or audit a channel's packaging. Human publishes: this skill never uploads or posts anything itself, and never downloads anyone's footage.
---

# YouTube Automation for Muse

You are operating a YouTube pipeline that **makes the videos and
packages them**. The system in one line: **videos rarely fail because
they are bad — they fail because nobody clicked, or clicked and
left.** Packaging (title, thumbnail, first seconds) is designed
BEFORE the video is finished, only moments with a proven outlier
pattern get made at all — and then the pipeline actually makes them:
cutting, formatting, captioning, and assembling the finished files
with ffmpeg.

Read `docs/packaging-playbook.md` before your first run. It is the
strategy; this file is the procedure.

## Setup (first run only)

1. Run `./setup.sh` (or check manually): Python 3.10+, Pillow, and
   ffmpeg must exist. Report what is missing instead of guessing.
2. Ask the user ONE question: **what niche?** Show them the built-in
   library — 28 presets in `config/niches/` (index:
   `config/niches/INDEX.md`; list them with
   `pipeline.niches.list_niches()`). If they are unsure, the three
   worked examples in `config/examples/` (gaming clips, bodycam/public
   footage, faceless facts) are the deep-dives to study.
3. Generate their config: copy the chosen preset (or
   `config/niche.example.yaml` for a custom niche) to
   `config/<their-niche>.yaml` and tune it WITH the user — winning
   types, reject list, cadence, subscribe line, and a canonical tag set
   built from the top videos in their niche (study 10–20 of them; do
   not invent tags from thin air). Read the preset's `sources`,
   `rights_note`, and `cautions` fields with the user before the first
   run — they define where this niche's footage legitimately comes
   from.
4. Confirm the user has: a YouTube channel, and footage they own or
   have the rights to use. If either is missing, stop and say so.

## The pipeline (every video, in order)

### 1. Pick niche — `config/niches/`
Work from the niche chosen in Setup: one of the 28 built-in presets
in `config/niches/` (catalog: `config/niches/INDEX.md`), or the
user's custom config. Its winning types, reject list, ship bar,
tag seeds, sources, and cautions drive every stage below — do not
run a video outside a picked niche.

### 2. Source
Gather the source footage the way the preset's `sources` field
describes: footage the user owns or has the rights to use, already
supplied as local files (see the preset's `rights_note`). Never
download, scrape, or rip footage from any platform — if the footage
isn't on the user's machine with rights cleared, stop here.

### 3. Select — `pipeline/select.py`
Watch the source footage and list candidate moments. Score each one
with `score_candidate` (five questions, 0–2 each, /10):

- Is the moment type one of the niche's proven winners?
- Is the hook in the FIRST frame?
- Does the working title create curiosity without spoiling the ending?
- Would a stranger finish it?
- Is it clearly better than the channel's average clip?

Ship only at the config's `min_ship_score` (default 8). Categories on
the reject list are hard-rejected at any score. **An empty slot beats
a weak video — never pad a run.**

### 4. Produce — `pipeline/produce.py`
Make the actual videos from the footage the user supplies locally.
Write a produce job (see `config/produce.example.json`): the source
file, the winning moments with their timestamps and scores, format,
and loudness. Then:

```bash
python3 -m pipeline.produce shorts config/<job>.json        # one Short per moment
python3 -m pipeline.produce compilation config/<job>.json   # one long video, best clip last
```

Production covers: frame-accurate cutting at the selected
timestamps, vertical 9:16 formatting for Shorts (blur-pad by
default, crop if the niche preset says so), burned captions from an
SRT (a source-timed SRT is sliced and re-timed automatically),
compilation assembly in countdown order — weakest winner first,
**best clip last** — and source audio kept as-is (`keep`) or
loudness-normalised (`safe`). Produce NEVER downloads footage and
never uploads anything; if the footage isn't already on the user's
machine with rights cleared (check the preset's `sources` and
`rights_note`), stop.

### 5. Package — `pipeline/seo.py`
Build the metadata pack with `build_pack` for each produced video:

- **Title**: curiosity up front, resolution withheld. If the title
  isn't clickable, the moment is wrong — go back to step 3.
- **Description**: hook line first (never a repeat of the title),
  subscribe line second, body, exact steps for secret/how-to videos,
  source credit, disclaimer, hashtags.
- **Tags**: video-specific tags first, then the niche canonical set,
  filled to ~490–500 characters, trimming generics from the end only.

### 6. Thumbnail — `pipeline/thumbnail.py`
Extract the rawest REAL frame from the finished video
(`extract_frame`) and treat it with `build_thumbnail`: saturated grade,
big display text (2–4 words, not a repeat of the title), heavy outline.
No AI-generated key art, no stock. The frame is a promise the video
must keep.

### 7. QC gate — `pipeline/qc.py`
Run `run_qc` on the score, the pack, and the thumbnail. **Every check
must pass.** A failure means fix the item or drop it — there is no
override, and you never report a failed item as ready.

### 8. Publish — HUMAN STEP
Uploading happens in YouTube Studio, by the user (or with the user
watching). Paste the pack, set the thumbnail, set the playlist, then
READ BACK the saved fields and confirm they match the pack before
calling the video published. Never claim a video is live from the
upload screen alone.

## Channel optimization (monthly, or on request)

Work through `docs/channel-optimization.md`: channel description
formula, channel keywords = the canonical tag set, and a per-video
audit of titles, descriptions, and tags. Change only what actually
falls short; verify by read-back.

## Honest limits — never break these

- **Rights**: only footage the user owns or has rights to use. Credit
  sources in every description. Reused-content and copyright rules are
  YouTube's, and they can end a channel — say so plainly when a plan
  leans on other people's footage.
- **No downloading**: the produce stage works only on files already
  on the user's machine, sourced the way their niche preset's
  `sources` field describes. Never fetch, rip, or scrape footage
  from any platform.
- **Safety edits**: in niches involving real people (e.g. bodycam),
  blur bystanders' faces, licence plates, and minors before publish.
- **No guarantees**: this pipeline applies patterns that correlate
  with outliers. It does not guarantee views, subscribers, or
  monetization, and you must never promise them.
- **No fake functionality**: steps that need the user's environment
  (Studio upload, analytics) are manual/assisted steps. Do not pretend
  an API call happened.
- **Metrics that matter**: judge results by average percentage viewed,
  average view duration, and impressions — not raw CTR or view counts.
  Study the channel's own outliers and make more of THAT pattern.
