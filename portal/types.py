"""Business datatypes for the returns portal."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Article:
    """A single article (line item) in an order."""

    sku: str
    name: str
    quantity: int
    quantity_returned: int
    price: float

    is_digital: bool = False
    is_final_sale: bool = False
    category: str = ""


@dataclass
class Order:
    """A mapped customer order."""

    order_number: str
    email: str
    recipient: str
    zip: str
    street: str
    city: str
    country_code: str
    order_locale: str
    order_date: datetime
    delivery_date: datetime
    articles: list[Article] = field(default_factory=list)

@dataclass(frozen=True)
class ReturnItem:
    """A validated article selected for return."""

    sku: str
    name: str
    qty: int
    price: float

@dataclass
class ArticleEligibility:
    """Result of evaluating return eligibility for a single article."""

    article: Article
    returnable: bool
    reason: str  # human-readable explanation (empty string when returnable)
    matched_rule: str  # identifier of the rule that matched (empty when returnable)
    
@dataclass
class EligibilityRuleBlock:
    """A single rule for determining return eligibility."""

    id: str
    reason: str
    reason_text: str = ""
    source: str = ""
    match: dict[str, str] = field(default_factory=dict)

@dataclass
class EligibilityRule:
    """A single rule for determining return eligibility."""

    id: str
    anchor_event: str
    anchor_event_offset_days: int
    return_window_days: int
    send_window_days: int
    loyalty_tier: str | None = None
    match: dict[str, str] = field(default_factory=dict)

@dataclass
class EligibilityRuleLegal:
    id: str
    return_window_min_days: int
    anchor_event: str
    anchor_offset_days: int
    match: dict[str, str] = field(default_factory=dict)

@dataclass
class EligibilityRuleLoyaltyTier:
    id: str
    loyalty_tier: str
    return_window_days: int
    anchor_event: str
    anchor_offset_days: int
    match: dict[str, str] = field(default_factory=dict)

@dataclass
class FinalSaleRule:
    allowed_countries: list[str] = field(default_factory=list)
    reason_text: dict[str, str] = field(default_factory=dict)

@dataclass
class EligibilityResult:
    eligible: bool
    resolved_return_window_days: int
    resolved_deadline: datetime
    applied_rules: list[str] = field(default_factory=list)
    final_rule_id: str = ""

@dataclass
class EligibilityRules:
    block: list[EligibilityRuleBlock] = field(default_factory=list)
    allow: list[EligibilityRule] = field(default_factory=list)
    legal: list[EligibilityRuleLegal] = field(default_factory=list)
    loyalty_tiers: list[EligibilityRule] = field(default_factory=list)
    final_sale: FinalSaleRule | None = None
    