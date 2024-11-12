from enum import Enum


class RoleEnum(str, Enum):
    # TODO: Add more
    MANAGERS = "managers"
    USER = "user"


class Permission(str, Enum):
    pass


class DocumentPermission(Permission):
    DOC_ACL = "doc_acl"
    DOC_READ = "doc_read"
    DOC_DELETE = "doc_delete"


class OrganizationPermission(Permission):
    ROLE_ACL = "role_acl"
    SUBJECT_NEW = "subject_new"
    SUBJECT_DOWN = "subject_down"
    SUBJECT_UP = "subject_up"
    DOC_NEW = "doc_new"


class RolePermission(Permission):
    ROLE_NEW = "role_new"
    ROLE_DOWN = "role_down"
    ROLE_UP = "role_up"
    ROLE_MOD = "role_mod"


# TODO: Set permissions map, this is just a placeholder (delivery 2)
permissions_map: dict[RoleEnum, list[Permission]] = {
    RoleEnum.MANAGERS: [
        DocumentPermission.DOC_ACL,
        DocumentPermission.DOC_READ,
        DocumentPermission.DOC_DELETE,
        OrganizationPermission.ROLE_ACL,
        OrganizationPermission.SUBJECT_NEW,
        OrganizationPermission.SUBJECT_DOWN,
        OrganizationPermission.SUBJECT_UP,
        OrganizationPermission.DOC_NEW,
        RolePermission.ROLE_NEW,
        RolePermission.ROLE_DOWN,
        RolePermission.ROLE_UP,
        RolePermission.ROLE_MOD,
    ],
    RoleEnum.USER: [
        DocumentPermission.DOC_READ,
        OrganizationPermission.ROLE_ACL,
        OrganizationPermission.SUBJECT_NEW,
        OrganizationPermission.SUBJECT_DOWN,
        OrganizationPermission.SUBJECT_UP,
        OrganizationPermission.DOC_NEW,
    ],
}
