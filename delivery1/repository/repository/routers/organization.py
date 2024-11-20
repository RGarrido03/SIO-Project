from fastapi import APIRouter
from starlette.requests import Request

from repository.crud.organization import crud_organization
from repository.crud.subject import crud_subject
from repository.models.organization import (
    Organization,
    OrganizationCreate,
    OrganizationBase,
)
from repository.utils.encryption.loaders import load_public_key

router = APIRouter(prefix="/organization", tags=["Organization"])


@router.post("", response_model=OrganizationBase)
async def create_organization(
    organization_and_subject: OrganizationCreate,
    request: Request,
) -> Organization:
    subject = await crud_subject.create(organization_and_subject.subject)
    organization = await crud_organization.create(organization_and_subject.organization)
    await crud_organization.add_subject(
        organization.name, subject.subject.username, subject.public_key.id
    )
    request.state.public_key = load_public_key(subject.public_key.key)
    return organization


@router.get("")
async def list_organizations() -> list[Organization]:
    return await crud_organization.get_all()
