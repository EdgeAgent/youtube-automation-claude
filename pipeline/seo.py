"""SEO pack builder — titles, description, and tags for one video.

Produces the complete metadata pack the QC gate checks:

- **Title options**: curiosity-gap templates. The title front-loads the
  most intriguing element and withholds the resolution — it never gives
  away the ending.
- **Description**: hook line first, subscribe line second, then the body,
  optional step-by-step block (for "secret" style videos, the steps ARE
  the search value), source credit, fan/affiliation disclaimer, hashtags.
- **Tags**: video-specific tags first, then the niche's canonical set,
  filled to ~490–500 characters total (YouTube's limit is 500), trimming
  generic tags from the END only.
"""

from __future__ import annotations

from dataclasses import dataclass, field

TAG_CHAR_LIMIT = 500
TAG_CHAR_TARGET_MIN = 490

DEFAULT_SUBSCRIBE_LINE = "🔔 SUBSCRIBE for daily videos — new uploads every single day! 🚀"
DEFAULT_DISCLAIMER = (
    "Fan-made channel. Not affiliated with, endorsed by, or sponsored by "
    "the original creators or rights holders of the source material."
)

_TITLE_TEMPLATES = [
    "{moment} — Nobody Expected This",
    "He Tried {attempt}… It Went Wrong Fast",
    "{moment} in {niche_name} Is Unreal",
    "Top {count} {moment_plural} You Missed",
    "The {moment} Nobody Is Talking About",
    "{moment} — Watch What Happens Next",
]


@dataclass
class MetadataPack:
    title: str
    title_options: list = field(default_factory=list)
    description: str = ""
    tags: list = field(default_factory=list)
    tag_chars: int = 0


def title_options(moment: str, niche_name: str = "this niche", count: int = 10,
                  attempt: str = "the Impossible", moment_plural: str | None = None) -> list[str]:
    """Generate curiosity-gap title options from templates.

    These are starting points, not finished titles: pick one, then sharpen
    it by hand. A title that names the ending is a failed title.
    """
    moment_plural = moment_plural or (moment + "s")
    options = []
    for template in _TITLE_TEMPLATES:
        options.append(template.format(
            moment=moment, niche_name=niche_name, count=count,
            attempt=attempt, moment_plural=moment_plural,
        ))
    return options


def build_tags(video_specific: list[str], canonical: list[str],
               limit: int = TAG_CHAR_LIMIT) -> list[str]:
    """Fill tags to just under the character limit.

    Order matters: video-specific tags first (they carry the search
    intent for THIS video), then the niche canonical set. Duplicates are
    dropped case-insensitively. When the limit is hit, remaining generic
    tags are trimmed from the end — specific tags are never dropped to
    make room for generics.
    """
    seen: set[str] = set()
    tags: list[str] = []
    chars = 0
    for raw in list(video_specific) + list(canonical):
        tag = raw.strip()
        key = tag.lower()
        if not tag or key in seen:
            continue
        cost = len(tag) + (2 if tags else 0)  # ", " separator as Studio counts it
        if chars + cost > limit:
            continue
        seen.add(key)
        tags.append(tag)
        chars += cost
    return tags


def tag_char_count(tags: list[str]) -> int:
    """Character count the way YouTube Studio counts a tag list."""
    return len(", ".join(tags))


def build_description(hook_line: str, body: str, credit: str,
                      subscribe_line: str = DEFAULT_SUBSCRIBE_LINE,
                      disclaimer: str = DEFAULT_DISCLAIMER,
                      steps: list[str] | None = None,
                      hashtags: list[str] | None = None) -> str:
    """Assemble a description in the fixed winning order.

    1. Hook line (never a repeat of the title)
    2. Subscribe line
    3. Body
    4. Steps, if the video is a "secret/how-to" type — exact steps are
       what search rewards in that lane
    5. Credit to the source of the footage
    6. Disclaimer
    7. Hashtags
    """
    parts = [hook_line.strip(), subscribe_line.strip(), "", body.strip()]
    if steps:
        parts += ["", "HOW IT WORKS / THE STEPS:"]
        parts += [f"{i}. {step.strip()}" for i, step in enumerate(steps, 1)]
    parts += ["", f"Credit: {credit.strip()}", "", disclaimer.strip()]
    if hashtags:
        parts += ["", " ".join(h if h.startswith("#") else f"#{h}" for h in hashtags)]
    return "\n".join(parts)


def build_pack(title: str, moment: str, niche: dict, hook_line: str, body: str,
               credit: str, video_specific_tags: list[str],
               steps: list[str] | None = None, hashtags: list[str] | None = None) -> MetadataPack:
    """Build the full pack for one video from its niche config."""
    canonical = list(niche.get("canonical_tags", []))
    tags = build_tags(video_specific_tags, canonical)
    description = build_description(
        hook_line=hook_line,
        body=body,
        credit=credit,
        subscribe_line=niche.get("subscribe_line", DEFAULT_SUBSCRIBE_LINE),
        steps=steps,
        hashtags=hashtags if hashtags is not None else niche.get("hashtags", []),
    )
    return MetadataPack(
        title=title,
        title_options=title_options(moment, niche.get("niche", "this niche")),
        description=description,
        tags=tags,
        tag_chars=tag_char_count(tags),
    )
