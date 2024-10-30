from fastapi import APIRouter

from repository.crud.organization import crud_organization
from repository.crud.subject import crud_subject
from repository.models.organization import (
    Organization,
    OrganizationCreate,
    OrganizationBase,
)

router = APIRouter(prefix="/organization", tags=["Organization"])


@router.post("", response_model=OrganizationBase)
async def create_organization(
    organization_and_subject: OrganizationCreate,
) -> Organization:
    subject = await crud_subject.create(organization_and_subject.subject)
    organization = await crud_organization.create(organization_and_subject.organization)
    await crud_organization.add_subject(
        organization.name, subject.subject.username, subject.public_key_id.id
    )
    return organization


@router.get("")
async def list_organizations() -> list[Organization]:
    return await crud_organization.get_all()
