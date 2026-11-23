"""Pre-publish QC gate — a failing item does not ship. Ever.

The discipline: a slot stays empty rather than shipping a weak video.
This module is the checklist that enforces it. ``run_qc`` returns a
report; ``passed`` is True only when EVERY check passes. There is no
override flag — fix the item or drop it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from . import seo as seo_mod
from . import select as select_mod
from . import thumbnail as thumb_mod


@dataclass
class QCItem:
    name: str
    passed: bool
    detail: str


@dataclass
class QCReport:
    items: list = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(item.passed for item in self.items)

    @property
    def failures(self) -> list:
        return [item for item in self.items if not item.passed]

    def summary(self) -> str:
        lines = [f"{'PASS' if item.passed else 'FAIL'}  {item.name}: {item.detail}"
                 for item in self.items]
        verdict = "QC PASSED — cleared to publish" if self.passed else \
            "QC FAILED — do not publish; fix or drop this item"
        return "\n".join(lines + ["", verdict])


def run_qc(score: select_mod.ScoreResult,
           pack: seo_mod.MetadataPack,
           thumbnail_path: str | Path | None,
           thumbnail_result: thumb_mod.ThumbnailResult | None = None,
           title_spoils_ending: bool = False) -> QCReport:
    """Run every pre-publish check for one video. Pure except file stats."""
    items: list[QCItem] = []

    items.append(QCItem(
        "winner_score",
        score.ship,
        f"score {score.total}/10" + ("" if score.ship else f" — {'; '.join(score.reasons)}"),
    ))

    items.append(QCItem(
        "title_present",
        bool(pack.title.strip()),
        pack.title or "title is empty",
    ))
    items.append(QCItem(
        "title_no_spoiler",
        not title_spoils_ending,
        "title withholds the ending" if not title_spoils_ending
        else "title gives away the ending — rewrite it",
    ))

    desc_lines = [line for line in pack.description.splitlines() if line.strip()]
    items.append(QCItem(
        "description_hook_first",
        len(desc_lines) >= 2 and "SUBSCRIBE" in desc_lines[1].upper(),
        "hook line first, subscribe line second" if len(desc_lines) >= 2
        and "SUBSCRIBE" in desc_lines[1].upper()
        else "description must open with the hook line, then the subscribe line",
    ))
    items.append(QCItem(
        "description_credit_and_disclaimer",
        "Credit:" in pack.description and "Not affiliated" in pack.description,
        "source credit + disclaimer present" if "Credit:" in pack.description
        and "Not affiliated" in pack.description
        else "description is missing the source credit or the disclaimer",
    ))

    items.append(QCItem(
        "tags_filled",
        seo_mod.TAG_CHAR_TARGET_MIN <= pack.tag_chars <= seo_mod.TAG_CHAR_LIMIT,
        f"{pack.tag_chars} chars (target {seo_mod.TAG_CHAR_TARGET_MIN}–{seo_mod.TAG_CHAR_LIMIT})",
    ))

    if thumbnail_path is None:
        items.append(QCItem("thumbnail_exists", False, "no thumbnail built"))
    else:
        exists = Path(thumbnail_path).exists()
        items.append(QCItem(
            "thumbnail_exists", exists,
            str(thumbnail_path) if exists else f"{thumbnail_path} not found",
        ))
        if thumbnail_result is not None:
            items.append(QCItem(
                "thumbnail_safe_zone",
                thumbnail_result.layout.in_safe_zone,
                "text inside the safe zone" if thumbnail_result.layout.in_safe_zone
                else "thumbnail text crosses the safe zone",
            ))
            items.append(QCItem(
                "thumbnail_legible",
                thumbnail_result.layout.legible_at_preview,
                f"text is {thumbnail_result.layout.preview_text_px:.0f}px tall at feed size"
                if thumbnail_result.layout.legible_at_preview
                else "thumbnail text is too small to read at feed size",
            ))

    return QCReport(items=items)
