from pipeline.niches import (
    list_niches,
    load_preset,
    preset_slugs,
    validate_preset,
)


def test_library_is_genuinely_big():
    assert len(preset_slugs()) >= 25


def test_every_preset_loads_complete_and_pipeline_ready():
    for slug in preset_slugs():
        cfg = load_preset(slug)
        assert validate_preset(cfg) == [], f"{slug} is incomplete"
        # the fields the stages actually consume
        assert cfg["min_ship_score"] == 8
        assert len(cfg["winning_types"]) >= 3
        assert len(cfg["canonical_tags"]) >= 4
        assert len(cfg["sources"]) >= 1
        assert len(cfg["cautions"]) >= 1


def test_catalog_summaries_cover_every_preset():
    catalog = list_niches()
    assert [entry["slug"] for entry in catalog] == preset_slugs()
    for entry in catalog:
        assert entry["niche"] and entry["summary"] and entry["format_lean"]


def test_known_presets_exist_with_their_signature_cautions():
    bodycam = load_preset("bodycam-police")
    assert any("Blur" in c for c in bodycam["cautions"])
    assert any("public" in s.lower() for s in bodycam["sources"])
    kids = load_preset("kids-family")
    assert any("Never" in c for c in kids["cautions"])


def test_missing_preset_raises_with_the_available_list():
    try:
        load_preset("underwater-basket-weaving")
    except FileNotFoundError as exc:
        assert "gaming-highlights" in str(exc)
    else:
        raise AssertionError("expected FileNotFoundError")
