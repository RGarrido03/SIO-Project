from fastapi import APIRouter

from repository.routers import organization, subject, document

router = APIRouter()
router.include_router(organization.router)
router.include_router(subject.router)
router.include_router(document.router)
