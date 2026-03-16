"""Main Router"""

from fastapi import APIRouter

from .feature_routes import admin_products
from .feature_routes import billing
from .feature_routes import purchases

router = APIRouter()

router.include_router(billing.router)
router.include_router(purchases.router)
router.include_router(admin_products.router)
