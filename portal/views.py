import json

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views import View

from portal.forms import LookupForm, ReturnForm
from portal.services.eligibility import evaluate_eligibility
from portal.services.order_store import find_order, get_order


class LookupView(View):
    """Order lookup page – validates order number + email / zip."""

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "returns/lookup.html", {"form": LookupForm()})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = LookupForm(request.POST)
        if form.is_valid():
            order = find_order(
                form.cleaned_data["order_number"],
                form.cleaned_data["identifier"],
            )
            if order is None:
                form.add_error(None, "Order not found or credentials do not match.")
            else:
                request.session["order_number"] = order.order_number
                return redirect("articles", order_number=order.order_number)

        return render(request, "returns/lookup.html", {"form": form})


class ArticlesView(View):
    """Articles page – shows items in the order with eligibility info."""

    def get(self, request: HttpRequest, order_number: str) -> HttpResponse:
        if request.session.get("order_number") != order_number:
            return redirect("lookup")

        order = get_order(order_number)
        if order is None:
            return redirect("lookup")
        
        sku_errors = request.session.pop("sku_errors", {})
        try:
            preserved = json.loads(request.session.pop("preserved_items", "{}"))
        except json.JSONDecodeError:
            preserved = {}

        results = evaluate_eligibility(order)
        article_rows = []
        for result in results:
            remaining_qty = max(
                result.article.quantity - result.article.quantity_returned,
                0,
            )
            
            preserved_qty = preserved.get(result.article.sku)
            
            article_rows.append(
                {
                    "result": result,
                    "remaining_qty": remaining_qty,
                    "quantity_options": list(range(1, remaining_qty + 1)),
                    "selectable": result.returnable and remaining_qty > 0,
                    "error": sku_errors.get(result.article.sku),
                    "preserved_qty": preserved_qty,
                }
            )

        return render(
            request,
            "returns/articles.html",
            {
                "order": order,
                "results": results,
                "article_rows": article_rows,
            },
        )

class ConfirmView(View):
    """Confirmation page – validates selection and shows summary."""

    def get(self, request: HttpRequest, order_number: str) -> HttpResponse:
        return redirect("articles", order_number=order_number)

    def post(self, request: HttpRequest, order_number: str) -> HttpResponse:
        if request.session.get("order_number") != order_number:
            return redirect("lookup")

        order = get_order(order_number)
        if order is None:
            return redirect("lookup")

        results = evaluate_eligibility(order)
        form = ReturnForm(request.POST, eligibility_results=results)

        if not form.is_valid():
            request.session["sku_errors"] = form.sku_errors
            request.session["preserved_items"] = request.POST.get("items", "{}")
            return redirect("articles", order_number=order_number)

        selected_items = form.cleaned_data["items"]
        items_json = json.dumps({item.sku: item.qty for item in selected_items})

        return render(
            request,
            "returns/confirm.html",
            {
                "order": order,
                "selected_items": selected_items,
                "items_json": items_json,
            },
        )
        
class SubmitView(View):
    """Processes the final return submission."""

    def post(self, request: HttpRequest, order_number: str) -> HttpResponse:
        if request.session.get("order_number") != order_number:
            return redirect("lookup")

        order = get_order(order_number)
        if order is None:
            return redirect("lookup")

        results = evaluate_eligibility(order)
        form = ReturnForm(request.POST, eligibility_results=results)

        if not form.is_valid():
            request.session["sku_errors"] = form.sku_errors
            request.session["preserved_items"] = request.POST.get("items", "{}")
            return redirect("articles", order_number=order_number)
        
        # TODO: Here you would typically process the return submission, e.g.,
        # save it to the database, send confirmation emails, etc.

        return redirect("success", order_number=order_number)


class SuccessView(View):
    """Success page – shown after a return is submitted."""

    def get(self, request: HttpRequest, order_number: str) -> HttpResponse:
        if request.session.get("order_number") != order_number:
            return redirect("lookup")

        request.session.pop("sku_errors", None)
        request.session.pop("preserved_items", None)

        # TODO: Display real follow up instructions based on the return process.
        # Clean up session data and show a success message.
        
        return render(
            request,
            "returns/success.html",
            {"order_number": order_number},
        )