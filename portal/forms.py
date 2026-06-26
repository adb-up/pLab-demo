import json

from django import forms

from portal.types import ArticleEligibility, ReturnItem


class LookupForm(forms.Form):
    """Order lookup form.

    The customer enters their order number and either the email address or zip
    code they used when placing the order.
    """

    order_number = forms.CharField(
        max_length=50,
        label="Order number",
        widget=forms.TextInput(
            attrs={"placeholder": "e.g. RMA-1001", "autofocus": True},
        ),
    )
    identifier = forms.CharField(
        max_length=100,
        label="Email or zip code",
        help_text="Enter the email address or zip code used for the order.",
        widget=forms.TextInput(attrs={"placeholder": "Email or zip code"}),
    )


class ReturnForm(forms.Form):
    items = forms.CharField(widget=forms.HiddenInput)

    def __init__(
        self,
        *args,
        eligibility_results: list[ArticleEligibility] | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._results_by_sku: dict[str, ArticleEligibility] = {
            r.article.sku: r for r in (eligibility_results or [])
        }
        self.sku_errors: dict[str, str] = {}

    def clean_items(self) -> list[ReturnItem]:
        raw = self.cleaned_data["items"]
        try:
            items: dict = json.loads(raw)
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid selection data.")

        if not isinstance(items, dict) or not items:
            raise forms.ValidationError("No items selected.")

        validated: list[ReturnItem] = []

        for sku, qty in items.items():
            error = self._validate_item(sku, qty)
            if error:
                self.sku_errors[sku] = error
            else:
                result = self._results_by_sku[sku]
                validated.append(
                    ReturnItem(
                        sku=sku,
                        name=result.article.name,
                        qty=int(qty),
                        price=result.article.price,
                    )
                )

        if self.sku_errors:
            raise forms.ValidationError("Some articles have errors.")

        return validated

    def _validate_item(self, sku: str, qty: int | str) -> str | None:
        result = self._results_by_sku.get(sku)
        if result is None:
            return "Unknown article."

        if not result.returnable:
            return f"{result.article.name} is not eligible for return."

        try:
            qty = int(qty)
        except (TypeError, ValueError):
            return "Invalid quantity."

        remaining = result.article.quantity - result.article.quantity_returned
        if qty < 1 or qty > remaining:
            return f"Cannot return {qty} — only {remaining} available."

        return None