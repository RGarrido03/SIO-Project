from fastapi import APIRouter

from repository.crud.organization import crud_organization
from repository.models.organization import Organization, OrganizationCreate

router = APIRouter(prefix="/organization")


@router.post("/")
async def create_organization(organization: OrganizationCreate) -> Organization:
    return await crud_organization.create(organization)


@router.get("/")
async def list_organizations() -> list[Organization]:
    return await crud_organization.get_all()
