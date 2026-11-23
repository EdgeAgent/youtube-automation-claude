from pathlib import Path

from pipeline.config import load_niche_config

ROOT = Path(__file__).resolve().parent.parent


def test_example_template_loads():
    cfg = load_niche_config(ROOT / "config" / "niche.example.yaml")
    assert cfg["min_ship_score"] == 8
    assert "fail" in cfg["winning_types"]
    assert "menu" in cfg["reject_types"]
    assert cfg["canonical_tags"]


def test_all_worked_examples_load():
    examples = sorted((ROOT / "config" / "examples").glob("*.yaml"))
    assert len(examples) == 3
    for path in examples:
        cfg = load_niche_config(path)
        assert cfg["niche"]
        assert cfg["winning_types"]
        assert cfg["canonical_tags"]
