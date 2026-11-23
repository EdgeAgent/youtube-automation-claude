"""The built-in niche library — pick a preset, don't start from blank.

``config/niches/`` ships a preset for every niche this pipeline is
commonly pointed at. A preset is an ordinary niche config in the
repo's flat YAML dialect (loaded by ``pipeline/config.py``), carrying
everything the stages read — winning/reject types, ship bar, cadence,
tag seeds, subscribe line — plus the guidance a human needs before
the first video: title and thumbnail style, where source footage for
that niche legitimately comes from, how it gets fed into the
pipeline, the rights note, and the niche's content cautions.

At setup the user either picks one of these or writes a custom
config from ``config/niche.example.yaml``. Picking a preset is the
fast path, not a straitjacket: copy it into ``config/`` under your
own name and tune it — the canonical tag set especially should be
rebuilt from the top videos in your corner of the niche.

The global rule stands over every preset: the toolkit never
downloads or scrapes other people's videos. Every preset's sources
are ways the *user* supplies footage they have the right to use.
"""

from __future__ import annotations

from pathlib import Path

from .config import load_niche_config

NICHE_DIR = Path(__file__).resolve().parent.parent / "config" / "niches"

# Fields every preset must carry. The pipeline stages read the first
# group; the second group is the guidance that keeps a new channel
# legal and on-brief.
PIPELINE_FIELDS = [
    "niche", "winning_types", "reject_types", "min_ship_score",
    "video_types", "cadence", "subscribe_line", "canonical_tags", "hashtags",
]
GUIDANCE_FIELDS = [
    "summary", "format_lean", "title_style", "thumbnail_style",
    "sources", "feed_method", "rights_note", "cautions",
]
REQUIRED_FIELDS = PIPELINE_FIELDS + GUIDANCE_FIELDS


def preset_slugs(directory: str | Path | None = None) -> list:
    """All preset slugs in the library, sorted."""
    folder = Path(directory) if directory is not None else NICHE_DIR
    return sorted(p.stem for p in folder.glob("*.yaml"))


def load_preset(slug: str, directory: str | Path | None = None) -> dict:
    """Load one preset by slug (e.g. 'bodycam-police') as a config dict."""
    folder = Path(directory) if directory is not None else NICHE_DIR
    path = folder / f"{slug}.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"No niche preset '{slug}'. Available: {', '.join(preset_slugs(folder))}"
        )
    return load_niche_config(path)


def list_niches(directory: str | Path | None = None) -> list:
    """Catalog summaries: slug, name, one-liner, and format lean per preset."""
    catalog = []
    for slug in preset_slugs(directory):
        cfg = load_preset(slug, directory)
        catalog.append({
            "slug": slug,
            "niche": cfg.get("niche", slug),
            "summary": cfg.get("summary", ""),
            "format_lean": cfg.get("format_lean", ""),
        })
    return catalog


def validate_preset(cfg: dict) -> list:
    """Return the list of required fields missing/empty in a preset."""
    return [f for f in REQUIRED_FIELDS if f not in cfg or cfg[f] in ("", [])]
