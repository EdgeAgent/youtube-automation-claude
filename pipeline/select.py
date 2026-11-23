"""Winner picker — score candidate moments, ship only the strong ones.

The rule this module encodes (see docs/packaging-playbook.md): in clip
niches, a small set of moment types produces almost all the outliers —
fails, funny moments, genuine reactions, and secrets shown with steps.
Everything else (menus, filler travel, no-payoff story beats) produces
almost nothing, no matter how well it is packaged.

Each candidate is scored on five questions, 0–2 points each, /10 total.
A candidate ships only at ``min_ship_score`` (default 8) AND only if its
category is not on the niche's reject list. Rejection is a hard gate,
not a low score: a rejected category never ships, however it is scored.
"""

from __future__ import annotations

from dataclasses import dataclass, field

DEFAULT_WINNING_TYPES = ["fail", "funny", "reaction", "secret"]
DEFAULT_REJECT_TYPES = [
    "menu",
    "shopping",
    "inventory",
    "filler_travel",
    "cutscene_no_payoff",
]
DEFAULT_MIN_SHIP_SCORE = 8


@dataclass
class MomentCandidate:
    """One candidate moment from a source video.

    The three 0–2 fields are human/agent judgements made while watching
    the moment; the booleans are observable facts about it.
    """

    title: str
    category: str
    hook_in_first_frame: bool
    title_curiosity: int  # 0-2: does the working title create curiosity without spoiling?
    stranger_would_finish: int  # 0-2
    better_than_channel_average: int  # 0-2
    start_s: float = 0.0
    end_s: float = 0.0
    notes: str = ""


@dataclass
class ScoreResult:
    candidate: MomentCandidate
    breakdown: dict = field(default_factory=dict)
    total: int = 0
    ship: bool = False
    reasons: list = field(default_factory=list)


def _clamp02(value: int) -> int:
    return max(0, min(2, int(value)))


def score_candidate(candidate: MomentCandidate, config: dict | None = None) -> ScoreResult:
    """Score one candidate against the niche config. Pure function."""
    config = config or {}
    winning = [t.lower() for t in config.get("winning_types", DEFAULT_WINNING_TYPES)]
    reject = [t.lower() for t in config.get("reject_types", DEFAULT_REJECT_TYPES)]
    min_ship = int(config.get("min_ship_score", DEFAULT_MIN_SHIP_SCORE))
    category = candidate.category.strip().lower()

    result = ScoreResult(candidate=candidate)

    if category in reject:
        result.breakdown = {"moment_type": 0}
        result.total = 0
        result.ship = False
        result.reasons.append(
            f"Hard reject: category '{category}' is on the niche reject list. "
            "These moments have no outlier track record — do not pad the run with one."
        )
        return result

    breakdown = {
        "moment_type": 2 if category in winning else 1,
        "hook_first_frame": 2 if candidate.hook_in_first_frame else 0,
        "title_curiosity": _clamp02(candidate.title_curiosity),
        "stranger_would_finish": _clamp02(candidate.stranger_would_finish),
        "better_than_average": _clamp02(candidate.better_than_channel_average),
    }
    total = sum(breakdown.values())
    result.breakdown = breakdown
    result.total = total

    if category not in winning:
        result.reasons.append(
            f"Category '{category}' is not one of the niche's proven winning types {winning}."
        )
    if not candidate.hook_in_first_frame:
        result.reasons.append("Hook is not in the first frame — re-cut so the tension starts at 0:00.")
    if breakdown["title_curiosity"] < 2:
        result.reasons.append("Title needs more curiosity without giving away the ending.")
    if breakdown["stranger_would_finish"] < 2:
        result.reasons.append("A stranger probably would not finish this — tighten or drop it.")
    if breakdown["better_than_average"] < 2:
        result.reasons.append("Not clearly better than the channel's average clip.")

    result.ship = total >= min_ship
    if not result.ship:
        result.reasons.append(f"Score {total}/10 is below the ship bar of {min_ship}. Rebuild or drop.")
    return result


def pick_winners(candidates: list[MomentCandidate], config: dict | None = None) -> list[ScoreResult]:
    """Score every candidate; return only the ones cleared to ship, best first."""
    results = [score_candidate(c, config) for c in candidates]
    return sorted((r for r in results if r.ship), key=lambda r: r.total, reverse=True)
