from pathlib import Path

from PIL import Image

from pipeline import qc, seo, thumbnail as th
from pipeline.select import MomentCandidate, score_candidate

CONFIG = {"winning_types": ["fail"], "reject_types": ["menu"], "min_ship_score": 8}
NICHE = {"niche": "test", "canonical_tags": ["a"] * 1, "hashtags": []}


def good_score():
    return score_candidate(MomentCandidate(
        title="T", category="fail", hook_in_first_frame=True,
        title_curiosity=2, stranger_would_finish=2, better_than_channel_average=2,
    ), CONFIG)


def good_pack():
    # Build a pack whose tags land in the 490-500 window.
    canonical = [f"canonical tag {i:02d} xyz" for i in range(30)]
    niche = dict(NICHE, canonical_tags=canonical)
    return seo.build_pack(
        title="The Flip — Nobody Expected This", moment="The Flip", niche=niche,
        hook_line="Calm water. Then chaos.", body="Body text.",
        credit="Channel owner footage.", video_specific_tags=["the flip"],
    )


def good_thumbnail(tmp_path):
    frame = tmp_path / "f.jpg"
    Image.new("RGB", (1280, 720), (10, 10, 10)).save(frame)
    out = tmp_path / "t.jpg"
    result = th.build_thumbnail(frame, ["WOW"], out)
    return out, result


def test_full_pass(tmp_path):
    out, result = good_thumbnail(tmp_path)
    report = qc.run_qc(good_score(), good_pack(), out, result)
    assert report.passed, report.summary()


def test_low_score_fails_gate(tmp_path):
    out, result = good_thumbnail(tmp_path)
    weak = score_candidate(MomentCandidate(
        title="T", category="fail", hook_in_first_frame=False,
        title_curiosity=0, stranger_would_finish=0, better_than_channel_average=0,
    ), CONFIG)
    report = qc.run_qc(weak, good_pack(), out, result)
    assert not report.passed
    assert any(i.name == "winner_score" for i in report.failures)


def test_missing_thumbnail_fails_gate():
    report = qc.run_qc(good_score(), good_pack(), Path("/nonexistent/thumb.jpg"))
    assert not report.passed


def test_spoiling_title_fails_gate(tmp_path):
    out, result = good_thumbnail(tmp_path)
    report = qc.run_qc(good_score(), good_pack(), out, result, title_spoils_ending=True)
    assert not report.passed
    assert any(i.name == "title_no_spoiler" for i in report.failures)


def test_underfilled_tags_fail_gate(tmp_path):
    out, result = good_thumbnail(tmp_path)
    pack = seo.build_pack(
        title="T", moment="M", niche=NICHE, hook_line="Hook.",
        body="Body.", credit="Owner.", video_specific_tags=["one tag"],
    )
    report = qc.run_qc(good_score(), pack, out, result)
    assert not report.passed
    assert any(i.name == "tags_filled" for i in report.failures)
