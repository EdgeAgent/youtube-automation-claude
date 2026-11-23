"""Minimal loader for niche config files.

The configs in ``config/`` are deliberately simple YAML: flat ``key: value``
pairs and string lists written as ``- item`` lines under a key. This loader
handles exactly that subset (plus ``#`` comments) with the standard library
only — no PyYAML dependency. Anything fancier belongs in a real YAML parser;
swap this out if your configs outgrow it.

Example::

    niche: gaming-clips
    winning_types:
      - fail
      - funny
    min_ship_score: 8
"""

from __future__ import annotations

import re
from pathlib import Path

_INT_RE = re.compile(r"^-?\d+$")
_FLOAT_RE = re.compile(r"^-?\d+\.\d+$")


def _scalar(raw: str):
    raw = raw.strip()
    if raw in ("true", "True"):
        return True
    if raw in ("false", "False"):
        return False
    if _INT_RE.match(raw):
        return int(raw)
    if _FLOAT_RE.match(raw):
        return float(raw)
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ("'", '"'):
        return raw[1:-1]
    return raw


def load_niche_config(path: str | Path) -> dict:
    """Load a flat niche config file into a dict."""
    config: dict = {}
    current_list_key: str | None = None

    for line in Path(path).read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and current_list_key is not None:
            config[current_list_key].append(_scalar(stripped[2:]))
            continue
        if ":" not in line:
            raise ValueError(f"Unsupported config line: {line!r}")
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value == "":
            config[key] = []
            current_list_key = key
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            config[key] = [_scalar(part) for part in inner.split(",")] if inner else []
            current_list_key = None
        else:
            config[key] = _scalar(value)
            current_list_key = None
    return config
