from pipeline import seo


def test_tags_fill_specific_first_and_stay_under_limit():
    specific = ["kayak fail", "river rescue"]
    canonical = [f"tag number {i} with some length" for i in range(60)]
    tags = seo.build_tags(specific, canonical)
    assert tags[:2] == specific
    assert seo.tag_char_count(tags) <= seo.TAG_CHAR_LIMIT


def test_tags_dedupe_case_insensitively():
    tags = seo.build_tags(["Fails"], ["fails", "FAILS", "funny"])
    assert tags == ["Fails", "funny"]


def test_tags_never_drop_specific_for_generic():
    specific = ["very specific niche tag"]
    canonical = ["x" * 480, "another generic"]
    tags = seo.build_tags(specific, canonical)
    assert tags[0] == "very specific niche tag"


def test_description_order_hook_subscribe_credit_disclaimer():
    desc = seo.build_description(
        hook_line="You have never seen a landing go this wrong.",
        body="Shot on the river last weekend.",
        credit="Filmed by the channel owner.",
        steps=["Go to the north ramp", "Wait for high tide"],
        hashtags=["kayak", "fails"],
    )
    lines = [l for l in desc.splitlines() if l.strip()]
    assert lines[0].startswith("You have never seen")
    assert "SUBSCRIBE" in lines[1]
    assert "Credit: Filmed by the channel owner." in desc
    assert "Not affiliated" in desc
    assert "1. Go to the north ramp" in desc
    assert desc.rstrip().endswith("#kayak #fails")


def test_title_options_are_curiosity_templates():
    options = seo.title_options("The River Flip", niche_name="kayak fishing")
    assert len(options) == len(seo._TITLE_TEMPLATES)
    assert any("River Flip" in o for o in options)


def test_build_pack_fills_tags_and_counts_chars():
    niche = {
        "niche": "kayak fishing",
        "canonical_tags": ["kayak fishing", "fishing fails", "kayak"],
        "subscribe_line": "🔔 SUBSCRIBE for daily kayak chaos! 🚀",
        "hashtags": ["kayak"],
    }
    pack = seo.build_pack(
        title="The River Flip — Nobody Expected This",
        moment="The River Flip",
        niche=niche,
        hook_line="The water was calm. Then it wasn't.",
        body="One cast, one flip.",
        credit="Filmed by the channel owner.",
        video_specific_tags=["river flip", "kayak fail"],
    )
    assert pack.tags[:2] == ["river flip", "kayak fail"]
    assert pack.tag_chars == seo.tag_char_count(pack.tags)
    assert pack.title_options
