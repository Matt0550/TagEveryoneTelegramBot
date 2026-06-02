from fastapi import APIRouter
from .groups import router as groups_router
from .admin_logs import router as admin_logs_router
from .auth import router as auth_router
from .lists import router as lists_router

router = APIRouter()

router.include_router(groups_router, prefix="/groups", tags=["Public Groups"])
router.include_router(admin_logs_router, prefix="/admin", tags=["Public Admin"])
router.include_router(auth_router)
router.include_router(lists_router)
