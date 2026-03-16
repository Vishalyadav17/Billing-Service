"""Admin routes for product CRUD and seeding"""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from ..db_operations.crud_ops.products import (
    create_product,
    delete_product,
    get_all_products,
    get_product_by_id,
    seed_default_products,
    update_product,
)
from ..db_operations.deps import get_db
from ..logger import logger
from ..templates import templates

router = APIRouter(prefix="/admin/products", tags=["admin-products"])


@router.get("", response_class=HTMLResponse)
def list_products(request: Request, db: Session = Depends(get_db), msg: str = ""):
    """List all products."""
    products = get_all_products(db)
    return templates.TemplateResponse(
        "admin/products.html",
        {"request": request, "products": products, "msg": msg},
    )


@router.post("/seed", response_class=RedirectResponse)
def seed_products(db: Session = Depends(get_db)):
    """Insert default seed products if they don't already exist."""
    count = seed_default_products(db)
    logger.info("seeded %d product(s)", count)
    return RedirectResponse(url=f"/admin/products?msg=Seeded+{count}+product(s).", status_code=303)


@router.post("/create", response_class=RedirectResponse)
def create_product_route(
    name: str = Form(...),
    product_code: str = Form(...),
    available_stocks: int = Form(...),
    price_per_unit: float = Form(...),
    tax_percentage: float = Form(...),
    db: Session = Depends(get_db),
):
    """Create a new product."""
    try:
        create_product(
            db,
            {
                "name": name.strip(),
                "product_code": product_code.strip().upper(),
                "available_stocks": available_stocks,
                "price_per_unit": price_per_unit,
                "tax_percentage": tax_percentage,
            },
        )
        return RedirectResponse(url="/admin/products?msg=Product+created.", status_code=303)
    except Exception as e:
        logger.error("create_product failed: %s", e)
        return RedirectResponse(url=f"/admin/products?msg=Error:+{str(e)}", status_code=303)


@router.get("/{product_id}/edit", response_class=HTMLResponse)
def edit_product_form(product_id: int, request: Request, db: Session = Depends(get_db)):
    """Render edit form for a product."""
    product = get_product_by_id(db, product_id)
    if not product:
        return RedirectResponse(url="/admin/products?msg=Product+not+found.", status_code=303)
    return templates.TemplateResponse("admin/product_form.html", {"request": request, "product": product})


@router.post("/{product_id}/update", response_class=RedirectResponse)
def update_product_route(
    product_id: int,
    name: str = Form(...),
    available_stocks: int = Form(...),
    price_per_unit: float = Form(...),
    tax_percentage: float = Form(...),
    db: Session = Depends(get_db),
):
    """Update an existing product."""
    update_product(
        db,
        product_id,
        {
            "name": name.strip(),
            "available_stocks": available_stocks,
            "price_per_unit": price_per_unit,
            "tax_percentage": tax_percentage,
        },
    )
    return RedirectResponse(url="/admin/products?msg=Product+updated.", status_code=303)


@router.post("/{product_id}/delete", response_class=RedirectResponse)
def delete_product_route(product_id: int, db: Session = Depends(get_db)):
    """Delete a product by ID."""
    deleted = delete_product(db, product_id)
    msg = "Product+deleted." if deleted else "Product+not+found."
    return RedirectResponse(url=f"/admin/products?msg={msg}", status_code=303)
