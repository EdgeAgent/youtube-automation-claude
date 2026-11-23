# YouTube Automation for Muse

A packaging-first YouTube pipeline for **any niche** — built to hand to
your AI agent (Meta Muse or any skill-reading agent), or to run
yourself from the command line.

It encodes one hard-won lesson: **videos don't fail because they're
bad — they fail on packaging.** Title, thumbnail, and the first seconds
decide whether anyone ever sees the content. So this pipeline designs
the packaging *first*, only makes moments that match proven winning
patterns, and refuses to ship anything that fails its QC gate.

## Quickstart

```bash
git clone <this-repo-url> youtube-automation-claude
cd youtube-automation-claude
./setup.sh
```

Then pick your path — full details in [INSTALL.md](INSTALL.md):

- **With an agent (recommended):** point it at [`SKILL.md`](SKILL.md),
  say your niche, and it sets everything up with you.
- **By hand:** copy `config/niche.example.yaml` to
  `config/<your-niche>.yaml`, fill it in, and drive the modules in
  `pipeline/` from Python.

## How the pipeline works

```
source footage ──► SELECT ──► PACKAGE ──► THUMBNAIL ──► QC GATE ──► you publish
                   score /10   titles,      real frame,    all checks   in Studio,
                   ship 8+     description, grade + type   must pass    verified
                               tags ~500
```

1. **Select** (`pipeline/select.py`) — candidate moments are scored on
   five questions (0–2 each, /10): winning moment type, hook in the
   first frame, title curiosity without spoiling, would a stranger
   finish it, better than the channel average. Ship only at 8+.
   Dead categories (menus, filler, no-payoff beats) are hard-rejected.
   *An empty slot beats a weak video.*
2. **Package** (`pipeline/seo.py`) — a full metadata pack per video:
   curiosity-gap title options, a description that opens with a hook
   line and a subscribe line (then body, steps for how-to/secret
   videos, source credit, disclaimer, hashtags), and tags filled to
   ~490–500 characters — video-specific first, niche canonical set
   after, generics trimmed from the end.
3. **Thumbnail** (`pipeline/thumbnail.py`) — a **real frame** from
   your own video, pulled with ffmpeg, given a saturated grade and
   bold outlined display text. Text is checked against a safe zone
   and for legibility at feed size. No AI key art, no stock photos.
4. **QC** (`pipeline/qc.py`) — the pre-publish gate. Score, title,
   description structure, tag fill, thumbnail checks: **every check
   must pass**, or the item is fixed or dropped. No override.
5. **Publish** — a human step, on purpose. You upload in YouTube
   Studio with the pack beside you, then read back the saved fields
   to confirm they match. (See `SKILL.md`, step 5.)

## Pick any niche

The niche is just a config file. `config/niche.example.yaml` is the
template; `config/examples/` ships three worked examples:

- **gaming clips** — fails, funny moments, reactions, secrets
- **bodycam / public footage** — chases, takedowns, K9 tracks
  (publicly released footage only; blur bystanders, plates, minors)
- **faceless facts** — countdowns, myth-busting, shocking facts

Your niche can be anything else: cooking disasters, woodworking saves,
kayak fishing, local history — if it has moments, it fits.

## The playbook

[`docs/packaging-playbook.md`](docs/packaging-playbook.md) is the
strategy guidebook the code enforces: packaging first, the metrics
that actually matter (average percentage viewed, average view
duration, impressions), outlier theory, uploading less and packaging
harder, and title craft. [`docs/channel-optimization.md`](docs/channel-optimization.md)
covers the channel level: description formula, channel keywords, and
the per-video audit.

## Setup you need

- A YouTube channel (yours).
- Footage you **own or have the rights to use**, and your own way of
  getting it into YouTube Studio (browser is fine).
- Python 3.10+, Pillow, ffmpeg. Nothing else.

## Honest limits

- **Copyright & reused content.** YouTube's reused-content policy is
  real and it ends channels. Use footage you own or have rights to,
  transform it with your own commentary/value, and credit sources.
  This repo does not make other people's footage safe to repost.
- **No guarantees.** These are patterns that correlate with outlier
  videos, drawn from studying what wins. They do not guarantee views,
  subscribers, or monetization — anyone who promises that is selling
  something.
- **No upload automation.** Nothing here logs into your account or
  posts for you. Publishing stays human, verified by read-back.

## Layout

```
SKILL.md / skill.yaml     the agent skill — hand the repo to your Muse
INSTALL.md                both install paths
setup.sh                  one-command environment check
config/                   niche template + worked examples
pipeline/                 select · seo · thumbnail · qc (+ config loader)
docs/                     the packaging playbook + channel optimization
tests/                    pytest suite — run: python3 -m pytest
```

## License

MIT — see [LICENSE](LICENSE).

## Credits

The packaging system is inspired by the Decoded Genius / Jake Bryant
packaging playbook (packaging first, outlier theory, upload less) and
by outlier research across top clip channels, generalized here for
any niche. Built by Edge Agency.
