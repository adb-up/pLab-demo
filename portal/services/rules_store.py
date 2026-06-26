"""Simple JSON-backed eligibility rules store.

Loads rules from ``portal/data/eligibility_rules_raw.json`` and provides
access to parsed rule sets used by the eligibility engine.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from portal.services.mapper import map_block_rule, map_eligibility_rule, map_legal_rule
from portal.types import EligibilityRules

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "eligibility_rules_raw.json"


def _load_raw() -> dict[str, Any]:
    with _DATA_PATH.open() as f:
        loaded: object = json.load(f)

    assert isinstance(loaded, dict), "rules JSON root must be an object"
    return cast(dict[str, Any], loaded)


def get_rules() -> EligibilityRules:
    raw = _load_raw()
    return EligibilityRules(
        block=[map_block_rule(r) for r in raw.get("eligibility_block", [])],
        allow=[map_eligibility_rule(r) for r in raw.get("base_window", [])],
        legal=[map_legal_rule(r) for r in raw.get("legal_base", [])],
        loyalty_tiers=[map_eligibility_rule(r) for r in raw.get("loyalty_tiers", [])],
    )
