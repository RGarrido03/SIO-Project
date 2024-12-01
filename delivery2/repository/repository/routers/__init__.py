from fastapi import APIRouter

from repository.routers import organization, subject, document, repository, role

router = APIRouter()
router.include_router(organization.router)
router.include_router(subject.router)
router.include_router(document.router)
router.include_router(repository.router)
router.include_router(role.router)
