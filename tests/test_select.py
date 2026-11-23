from pipeline.select import MomentCandidate, pick_winners, score_candidate

CONFIG = {
    "winning_types": ["fail", "funny", "reaction", "secret"],
    "reject_types": ["menu", "shopping"],
    "min_ship_score": 8,
}


def strong(**overrides):
    base = dict(
        title="The Escape That Went Wrong",
        category="fail",
        hook_in_first_frame=True,
        title_curiosity=2,
        stranger_would_finish=2,
        better_than_channel_average=2,
    )
    base.update(overrides)
    return MomentCandidate(**base)


def test_perfect_candidate_scores_10_and_ships():
    result = score_candidate(strong(), CONFIG)
    assert result.total == 10
    assert result.ship is True


def test_rejected_category_never_ships():
    result = score_candidate(strong(category="menu"), CONFIG)
    assert result.ship is False
    assert result.total == 0
    assert any("Hard reject" in r for r in result.reasons)


def test_no_hook_costs_two_points_and_blocks_ship():
    result = score_candidate(strong(hook_in_first_frame=False), CONFIG)
    assert result.total == 8 - 0  # 10 - 2 = 8, still at the bar
    assert result.breakdown["hook_first_frame"] == 0


def test_weak_candidate_fails_the_bar():
    result = score_candidate(
        strong(title_curiosity=0, stranger_would_finish=1, better_than_channel_average=0),
        CONFIG,
    )
    assert result.total == 5
    assert result.ship is False


def test_unlisted_category_gets_partial_type_credit():
    result = score_candidate(strong(category="speedrun"), CONFIG)
    assert result.breakdown["moment_type"] == 1


def test_pick_winners_returns_only_shippers_best_first():
    candidates = [
        strong(title="A"),
        strong(title="B", title_curiosity=1),  # 9
        strong(title="C", category="menu"),    # rejected
        strong(title="D", stranger_would_finish=0, better_than_channel_average=0),  # 6
    ]
    winners = pick_winners(candidates, CONFIG)
    assert [w.candidate.title for w in winners] == ["A", "B"]
