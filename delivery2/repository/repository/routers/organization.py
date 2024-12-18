from fastapi import APIRouter
from starlette.requests import Request

from repository.crud.organization import crud_organization
from repository.crud.subject import crud_subject
from repository.crud.subject_organization_link import crud_subject_organization_link
from repository.models.organization import (
    Organization,
    OrganizationCreate,
    OrganizationBase,
)
from repository.models.relations import SubjectOrganizationLinkCreate
from repository.utils.encryption.loaders import load_public_key

router = APIRouter(prefix="/organization", tags=["Organization"])


@router.post("", response_model=OrganizationBase, description="rep_create_org")
async def create_organization(
    organization_and_subject: OrganizationCreate,
    request: Request,
) -> Organization:
    subject = await crud_subject.create(organization_and_subject.subject)
    organization = await crud_organization.create(
        organization_and_subject.organization
    )
    await crud_subject_organization_link.create(
        SubjectOrganizationLinkCreate(
            organization_name=organization.name,
            subject_username=subject.subject.username,
            role_ids=["Managers"],
            public_key_id=subject.public_key.id,
        )
    )
    request.state.public_key = load_public_key(subject.public_key.key)
    return organization


@router.get("", description="rep_list_orgs")
async def list_organizations() -> list[Organization]:
    return await crud_organization.get_all()
