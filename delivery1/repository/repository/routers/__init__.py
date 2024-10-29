from fastapi import APIRouter

from repository.routers import organization, subject

router = APIRouter()
router.include_router(organization.router)
router.include_router(subject.router)
