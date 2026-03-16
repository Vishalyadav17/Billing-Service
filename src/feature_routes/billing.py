"""Billing page routes — form, bill generation and result display"""

import time
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from ..db_operations.crud_ops.bills import create_bill, get_bill_by_id
from ..db_operations.crud_ops.products import decrement_stock, get_product_by_code
from ..db_operations.deps import get_db
from ..logger import logger
from ..templates import templates
from ..utils.billing_calc import calculate_bill_items, calculate_change_denominations
from ..utils.constants import DENOMINATIONS
from ..utils.email_service import send_invoice_email

router = APIRouter(tags=["billing"])


@router.get("/billing", response_class=HTMLResponse)
def billing_page(request: Request, db: Session = Depends(get_db), bill_id: int = None, error: str = ""):
    """Render the billing form. If bill_id is present, also show the generated bill result."""
    bill = None

    if bill_id:
        bill = get_bill_by_id(db, bill_id)
        if not bill:
            error = f"Bill #{bill_id} not found."

    return templates.TemplateResponse(
        "billing.html",
        {"request": request, "bill": bill, "denominations": DENOMINATIONS, "error": error},
    )


@router.post("/billing/generate", response_class=RedirectResponse)
async def generate_bill(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    customer_email: str = Form(...),
    cash_paid: float = Form(...),
    product_codes: List[str] = Form(...),
    quantities: List[int] = Form(...),
    denom_500: int = Form(0),
    denom_50: int = Form(0),
    denom_20: int = Form(0),
    denom_10: int = Form(0),
    denom_5: int = Form(0),
    denom_2: int = Form(0),
    denom_1: int = Form(0),
):
    """Validate products, calculate totals, persist the bill and trigger invoice email in background."""
    start = time.time()
    logger.info("Input: email=%s, products=%s, qty=%s", customer_email, product_codes, quantities)

    if len(product_codes) != len(quantities):
        return RedirectResponse(url="/billing?error=Mismatched+product+and+quantity+count.", status_code=303)

    products_with_qty = []
    for code, qty in zip(product_codes, quantities):
        code = code.strip().upper()
        if not code or qty <= 0:
            continue
        product = get_product_by_code(db, code)
        if not product:
            return RedirectResponse(url=f"/billing?error=Product+'{code}'+not+found.", status_code=303)
        if product.available_stocks < qty:
            return RedirectResponse(
                url=f"/billing?error=Insufficient+stock+for+'{code}'.+Available:+{product.available_stocks}",
                status_code=303,
            )
        products_with_qty.append((product, qty))

    if not products_with_qty:
        return RedirectResponse(url="/billing?error=No+valid+products+added.", status_code=303)

    items, total_without_tax, total_tax, net_price, rounded_net_price = calculate_bill_items(products_with_qty)

    if cash_paid < rounded_net_price:
        return RedirectResponse(
            url=f"/billing?error=Cash+paid+({cash_paid:.2f})+is+less+than+bill+amount+({rounded_net_price:.2f}).",
            status_code=303,
        )

    balance = round(cash_paid - rounded_net_price, 2)

    denominations_available = {
        500: denom_500, 50: denom_50, 20: denom_20,
        10: denom_10, 5: denom_5, 2: denom_2, 1: denom_1,
    }
    denominations_given = calculate_change_denominations(balance, denominations_available)

    for product, qty in products_with_qty:
        decrement_stock(db, product.id, qty)

    bill = create_bill(
        db,
        {
            "customer_email": customer_email.lower().strip(),
            "total_without_tax": total_without_tax,
            "total_tax": total_tax,
            "net_price": net_price,
            "rounded_net_price": rounded_net_price,
            "cash_paid": cash_paid,
            "balance": balance,
            "denominations_available": {str(k): v for k, v in denominations_available.items()},
            "denominations_given": {str(k): v for k, v in denominations_given.items()},
            "items": items,
        },
    )

    background_tasks.add_task(send_invoice_email, {
        "bill_id": bill.id,
        "customer_email": bill.customer_email,
        "total_without_tax": bill.total_without_tax,
        "total_tax": bill.total_tax,
        "net_price": bill.net_price,
        "rounded_net_price": bill.rounded_net_price,
        "cash_paid": bill.cash_paid,
        "balance": bill.balance,
        "items": items,
    })

    logger.debug("Output: Time taken - %s s, bill_id - %s", round(time.time() - start, 2), bill.id)
    return RedirectResponse(url=f"/billing?bill_id={bill.id}", status_code=303)
