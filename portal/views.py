import json

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views import View

from portal.forms import LookupForm, ReturnForm
from portal.services.eligibility import evaluate_eligibility
from portal.services.order_store import find_order, get_order, update_returned_quantities


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
        
        if request.GET.get("returnable_only") == "true":
            request.session["returnable_only"] = True
        elif request.GET.get("returnable_only") == "false":
            request.session["returnable_only"] = False
            

        for result in results:
            if request.session.get("returnable_only", False) and not result.returnable:
                continue
            
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
            
        if request.headers.get("HX-Request"):
            return render(
                request,
                "returns/_article_list.html",
                {"article_rows": article_rows},
            )

        return render(
            request,
            "returns/articles.html",
            {
                "order": order,
                "results": results,
                "article_rows": article_rows,
                "returnable_only": request.session.get("returnable_only", False),
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
        
        # TODO: add a service layer for orders, the views should work with the service layer, not directly with the data store.
        update_returned_quantities(order_number, form.cleaned_data["items"])

        return redirect("success", order_number=order_number)


class SuccessView(View):
    """Success page – shown after a return is submitted."""

    def get(self, request: HttpRequest, order_number: str) -> HttpResponse:
        if request.session.get("order_number") != order_number:
            return redirect("lookup")

        request.session.pop("sku_errors", None)
        request.session.pop("preserved_items", None)
        
        # TODO: cleanup order data and user information from session
        # TODO: keep returnable_only as session data or clear it after success? For now, we clear it.
        request.session.pop("returnable_only", None)

        # TODO: Display real follow up instructions based on the return process.
        # Clean up session data and show a success message.
        
        return render(
            request,
            "returns/success.html",
            {"order_number": order_number},
        )