# Changelog

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
