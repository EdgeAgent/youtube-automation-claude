# Install

Two ways in. Both end at the same place: a niche config that is yours,
and a pipeline you run video by video.

**Requirements** (both paths): Python 3.10+, [Pillow](https://pillow.readthedocs.io/),
and [ffmpeg](https://ffmpeg.org/) on your PATH. That's it — the pipeline
itself is standard library + Pillow. pytest is optional, for the tests.

---

## Path A — "Give it to your Muse" (recommended)

This repo is a one-shot package for an AI agent (Meta Muse, or any
agent that reads skill files):

1. Clone or download this repo.
2. Open your agent in the repo folder and point it at **`SKILL.md`**
   (the skill is also registered in `skill.yaml`).
3. Say your niche — *"I want to run a channel about kayak fishing
   fails"* is enough.
4. The agent runs `./setup.sh`, checks your environment, then sets up
   your niche config with you — starting from the built-in library
   of 28 presets in `config/niches/` (or `config/niche.example.yaml`
   for a custom niche), studying the top videos in your niche for
   the tag set.
5. From there it runs the pipeline per video: select → produce →
   package → thumbnail → QC. Production happens on your machine,
   from footage you supply. You do the final upload in YouTube
   Studio; the agent prepares everything and verifies the result
   with you.

## Path B — Plain CLI

```bash
git clone <this-repo-url> youtube-automation-claude
cd youtube-automation-claude
./setup.sh                      # environment check + next steps

# optional: keep dependencies isolated
python3 -m venv .venv && source .venv/bin/activate
pip install Pillow pytest

# your niche — pick a preset from the built-in library, or start custom
cp config/niches/gaming-highlights.yaml config/my-niche.yaml   # then edit it
# (custom instead: cp config/niche.example.yaml config/my-niche.yaml)

# run the tests to see the machinery work
python3 -m pytest

# make a video: copy the example job, point it at YOUR footage, run it
cp config/produce.example.json config/my-job.json              # then edit it
python3 -m pipeline.produce shorts config/my-job.json          # or: compilation
```

Then use the modules directly from Python:

```python
from pipeline.config import load_niche_config
from pipeline.niches import load_preset
from pipeline.select import MomentCandidate, score_candidate
from pipeline.produce import load_job, produce_shorts, produce_compilation
from pipeline.seo import build_pack
from pipeline.thumbnail import extract_frame, build_thumbnail
from pipeline.qc import run_qc

niche = load_niche_config("config/my-niche.yaml")   # or load_preset("bodycam-police")
job = load_job("config/my-job.json")
produce_shorts(job)          # cut + vertical-format + caption every winner
# ...build the pack, build the thumbnail, run QC.
# Publish by hand in YouTube Studio — see SKILL.md, step 6.
```

## What is NOT installed

Nothing here uploads to YouTube, logs into your account, or calls the
YouTube API — and nothing downloads footage either; production works
only on files you supply. Publishing is a deliberate human step
(SKILL.md step 6). That is a design choice, not a missing feature:
the pipeline's job is that everything you paste into Studio is
already produced, packaged, and QC'd.
