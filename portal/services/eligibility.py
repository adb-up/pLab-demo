"""Return eligibility engine."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Protocol, TypeVar

from portal.services.rules_store import get_rules
from portal.types import (
    Article,
    ArticleEligibility,
    EligibilityResult,
    EligibilityRule,
    EligibilityRuleBlock,
    EligibilityRuleLegal,
    EligibilityRules,
    FinalSaleRule,
    Order,
)

DIMENSION_RANK = ["country", "category", "tier"]

T = TypeVar("T")


class HasMatch(Protocol):
    match: dict[str, str]


def matches(match: dict[str, Any], context: dict[str, Any]) -> bool:
    for k, v in match.items():
        ctx_val = context.get(k)
        if isinstance(v, list):
            if ctx_val not in v:
                return False
        elif ctx_val != v:
            return False
    return True


def specificity(match: dict[str, Any]) -> int:
    return len(match)


def tiebreak_key(match: dict[str, Any]) -> tuple[int, ...]:
    return tuple(0 if dim in match else 1 for dim in DIMENSION_RANK)


def best_match(rules: list[T], context: dict[str, Any]) -> T | None:
    candidates = [(r, r.match) for r in rules if matches(r.match, context)]  # type: ignore[attr-defined]
    if not candidates:
        return None
    candidates.sort(key=lambda pair: (-specificity(pair[1]), tiebreak_key(pair[1])))
    return candidates[0][0]


def resolve_eligibility(article: Article, order: Order, rules: EligibilityRules) -> EligibilityResult:
    context: dict[str, Any] = {
        "category": article.category,
        "country": order.country_code,
        "delivery_date": order.delivery_date,
        "order_date": order.order_date,
    }

    applied_rules: list[str] = []

    blocked = [r for r in rules.block if matches(r.match, context)]
    if blocked:
        return EligibilityResult(
            eligible=False,
            resolved_return_window_days=0,
            resolved_deadline=order.delivery_date,
            applied_rules=[r.id for r in blocked],
            final_rule_id=blocked[0].id,
        )

    base = best_match(rules.allow, context)
    if base is None:
        return EligibilityResult(
            eligible=False,
            resolved_return_window_days=0,
            resolved_deadline=order.delivery_date,
            applied_rules=[],
            final_rule_id="",
        )

    window_days = base.return_window_days
    anchor_event = base.anchor_event
    anchor_offset = base.anchor_event_offset_days
    applied_rules.append(base.id)
    final_rule_id = base.id

    legal = best_match(rules.legal, context)
    if legal and window_days < legal.return_window_min_days:
        window_days = legal.return_window_min_days
        anchor_event = legal.anchor_event
        anchor_offset = legal.anchor_offset_days
        applied_rules.append(legal.id)
        final_rule_id = legal.id

    tier = best_match(rules.loyalty_tiers, context)
    if tier and tier.return_window_days > window_days:
        window_days = tier.return_window_days
        applied_rules.append(tier.id)
        final_rule_id = tier.id

    anchor_date: datetime = context.get(anchor_event, order.delivery_date)
    resolved_deadline = anchor_date + timedelta(days=anchor_offset + window_days)

    return EligibilityResult(
        eligible=True,
        resolved_return_window_days=window_days,
        resolved_deadline=resolved_deadline,
        applied_rules=applied_rules,
        final_rule_id=final_rule_id,
    )


def evaluate_eligibility(order: Order) -> list[ArticleEligibility]:
    rules = get_rules()
    results: list[ArticleEligibility] = []

    for article in order.articles:
        if article.is_digital:
            results.append(ArticleEligibility(
                article=article,
                returnable=False,
                reason="Digital items are not eligible for return.",
                matched_rule="digital_item",
            ))
            continue

        if article.is_final_sale:
            final_sale = rules.final_sale
            if final_sale and order.country_code in final_sale.allowed_countries:
                # TODO: Localize this message based on the user's locale or order locale if available
                # For now, we will use the English message as a default - as the interface is just in English.
                reason = final_sale.reason_text.get("en-US", "This item was marked as final sale and cannot be returned.")
                results.append(ArticleEligibility(
                    article=article,
                    returnable=False,
                    reason=reason,
                    matched_rule="final_sale",
                ))
                continue

        if article.quantity_returned >= article.quantity:
            results.append(ArticleEligibility(
                article=article,
                returnable=False,
                reason="All units have already been returned.",
                matched_rule="already_returned",
            ))
            continue

        result = resolve_eligibility(article, order, rules)

        if not result.eligible:
            blocked_rule = next((r for r in rules.block if r.id == result.final_rule_id), None)
            reason = (blocked_rule.reason_text if blocked_rule and blocked_rule.reason_text
                      else f"Blocked by rule: {result.final_rule_id}")
            results.append(ArticleEligibility(
                article=article,
                returnable=False,
                reason=reason,
                matched_rule=result.final_rule_id,
            ))
            continue

        now = datetime.now()
        if now > result.resolved_deadline:
            results.append(ArticleEligibility(
                article=article,
                returnable=False,
                reason=f"Return window expired on {result.resolved_deadline.strftime('%b %d, %Y')}.",
                matched_rule=result.final_rule_id,
            ))
            continue

        results.append(ArticleEligibility(
            article=article,
            returnable=True,
            reason="",
            matched_rule=result.final_rule_id,
        ))

    return results
