"""Load the grounded data assets. Pure I/O, no side effects."""
from __future__ import annotations

import json
from functools import lru_cache
from typing import Any, Dict

from . import config


def _read_json(path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


@lru_cache(maxsize=None)
def load_profile() -> Dict[str, Any]:
    """Connector-grounded Kisunla drug profile."""
    return _read_json(config.PROFILE_FILE)


@lru_cache(maxsize=None)
def load_competitors() -> Dict[str, Any]:
    """Competitor + market landscape (competitor facts verify-before-use)."""
    return _read_json(config.COMPETITOR_FILE)


@lru_cache(maxsize=None)
def load_payers() -> Dict[str, Any]:
    """Payer / CMS-CED market-access intelligence."""
    return _read_json(config.PAYER_FILE)


def load_all() -> Dict[str, Any]:
    return {
        "profile": load_profile(),
        "competitors": load_competitors(),
        "payers": load_payers(),
    }
