from pathlib import Path

from PIL import Image

from pipeline import thumbnail as th


def test_small_text_is_legible_at_preview():
    layout = th.plan_text_layout(["HE RAN"], font_size=120)
    assert layout.legible_at_preview is True
    assert layout.preview_text_px >= th.MIN_PREVIEW_TEXT_PX


def test_huge_text_breaks_safe_zone():
    layout = th.plan_text_layout(["A VERY LONG LINE OF THUMBNAIL TEXT HERE"], font_size=200)
    assert layout.in_safe_zone is False


def test_fit_text_layout_shrinks_until_it_fits():
    layout = th.fit_text_layout(["A VERY LONG LINE OF THUMBNAIL TEXT HERE", "SECOND LINE"])
    assert layout.in_safe_zone is True
    assert layout.font_size < 200


def test_bottom_anchor_respects_bottom_margin():
    layout = th.plan_text_layout(["SHORT"], font_size=100, anchor="bottom-left")
    assert layout.box[3] == th.THUMB_H - th.SAFE_MARGIN
    assert layout.box[0] == th.SAFE_MARGIN


def test_build_thumbnail_from_real_frame(tmp_path):
    frame = tmp_path / "frame.jpg"
    Image.new("RGB", (1920, 1080), (30, 60, 120)).save(frame)
    out = tmp_path / "thumb.jpg"
    result = th.build_thumbnail(frame, ["IT GOT", "REAL"], out)
    assert Path(result.out_path).exists()
    with Image.open(out) as img:
        assert img.size == (1280, 720)
    assert result.font_used  # a font (or the documented fallback) was used
