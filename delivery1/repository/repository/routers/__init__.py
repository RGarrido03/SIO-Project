from fastapi import APIRouter

from repository.routers import organization

router = APIRouter()
router.include_router(organization.router)
