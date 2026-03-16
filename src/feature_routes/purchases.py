"""Purchase history routes"""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from ..db_operations.crud_ops.bills import get_bill_by_id, get_bills_by_email
from ..db_operations.deps import get_db
from ..logger import logger
from ..templates import templates

router = APIRouter(tags=["purchases"])


@router.get("/purchases", response_class=HTMLResponse)
def purchases_page(request: Request, email: str = "", db: Session = Depends(get_db)):
    """Show purchase history for a given customer email."""
    bills = []
    if email:
        bills = get_bills_by_email(db, email)
        logger.info("Input: email=%s, found=%d", email, len(bills))
    return templates.TemplateResponse(
        "purchases.html",
        {"request": request, "bills": bills, "searched_email": email},
    )


@router.post("/purchases/search", response_class=RedirectResponse)
def search_purchases(email: str = Form(...)):
    """Redirect to purchase history page with the searched email as query param."""
    return RedirectResponse(url=f"/purchases?email={email.strip()}", status_code=303)


@router.get("/purchases/{bill_id}", response_class=HTMLResponse)
def purchase_detail(bill_id: int, request: Request, db: Session = Depends(get_db)):
    """Show full detail of a single purchase."""
    bill = get_bill_by_id(db, bill_id)
    if not bill:
        return templates.TemplateResponse(
            "purchases.html",
            {"request": request, "bills": [], "searched_email": "", "error": f"Purchase #{bill_id} not found."},
        )
    return templates.TemplateResponse("purchase_detail.html", {"request": request, "bill": bill})
