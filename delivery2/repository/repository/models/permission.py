from enum import Enum


class Permission(str, Enum):
    pass


class DocumentPermission(Permission):
    DOC_ACL = "DOC_ACL"
    DOC_READ = "DOC_READ"
    DOC_DELETE = "DOC_DELETE"


class OrganizationPermission(Permission):
    ROLE_ACL = "ROLE_ACL"
    SUBJECT_NEW = "SUBJECT_NEW"
    SUBJECT_DOWN = "SUBJECT_DOWN"
    SUBJECT_UP = "SUBJECT_UP"
    DOC_NEW = "DOC_NEW"


class RolePermission(Permission):
    ROLE_NEW = "ROLE_NEW"
    ROLE_DOWN = "ROLE_DOWN"
    ROLE_UP = "ROLE_UP"
    ROLE_MOD = "ROLE_MOD"


all_permissions = [
    perm
    for perm_group in [DocumentPermission, OrganizationPermission, RolePermission]
    for perm in perm_group
]
