# Changelog

## v0.2.0 — 2026-11-23

The pipeline now **makes the videos**, not just the packaging.

- **Production** (`pipeline/produce.py`): an ffmpeg-based stage that
  turns the winner picker's selected moments into finished videos —
  frame-accurate clip cutting, vertical 9:16 Shorts formatting
  (blur-pad or crop), burned captions from SRT (source-timed SRTs
  are sliced and re-timed automatically), compilation assembly with
  the best clip last, and loudness-safe audio (`loudnorm` toward
  -14 LUFS) or untouched source audio. Ships with a CLI
  (`python3 -m pipeline.produce cut|shorts|compilation|shift-captions`)
  and an example job file (`config/produce.example.json`). Works
  only on footage the user supplies locally — no downloading, no
  scraping, no uploading.
- **Niche library** (`config/niches/` + `pipeline/niches.py`):
  28 built-in presets (gaming, bodycam, sports, true crime, cooking,
  finance, dashcam, courtroom, and 20 more). Each preset carries the
  pipeline fields plus title/thumbnail style, **its own sources**
  (where that niche's footage legitimately comes from and how it is
  fed in), a rights note, and content cautions. Catalog index at
  `config/niches/INDEX.md`.
- **Docs consistency pass**: README, SKILL.md, INSTALL.md, the
  playbook, and the config template all describe the same six
  stages — select → produce → package → thumbnail → QC → publish —
  and the README gallery is now a "Watch it work" section linking
  the real, live videos.
- Tests: 51 passing (production and niche-library suites added).

## v0.1.0 — 2026-11-23

First public release.

- **Pipeline** (`pipeline/`): winner-only moment selection with a
  /10 self-score and an 8+ ship bar (`select.py`); full SEO packs —
  curiosity-gap titles, hook-first descriptions, tags filled to
  ~490–500 chars (`seo.py`); thumbnails built from real frames of
  your own video with safe-zone and legibility checks
  (`thumbnail.py`); a pre-publish QC gate with no override (`qc.py`);
  a stdlib-only niche config loader (`config.py`).
- **Niche system** (`config/`): a fill-in template plus three worked
  examples — gaming clips, bodycam/public footage, faceless facts.
- **Agent skill** (`SKILL.md` + `skill.yaml`): hand the repo to your
  Muse (or another agent) and it runs setup, niche selection, and
  every pipeline stage with you.
- **Docs**: the packaging playbook (packaging first, APV/AVD/
  impressions, outlier theory, upload less, title craft) and the
  channel-optimization checklist.
- **Install**: two paths in `INSTALL.md`, plus `./setup.sh`, a
  one-command environment check (Python / Pillow / ffmpeg).
- Tests: pytest suite covering selection scoring, tag filling,
  description structure, thumbnail layout, the QC gate, and config
  loading.
