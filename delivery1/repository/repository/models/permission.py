from enum import Enum


class RoleEnum(str,Enum):
    # TODO: Add more
    MANAGERS = "managers"
    USER = "user"


class DocumentPermission(str,Enum):
    DOC_ACL = "doc_acl"
    DOC_READ = "doc_read"
    DOC_DELETE = "doc_delete"


class OrganizationPermission(Enum):
    ROLE_ACL = "role_acl"
    SUBJECT_NEW = "subject_new"
    SUBJECT_DOWN = "subject_down"
    SUBJECT_UP = "subject_up"
    DOC_NEW = "doc_new"


class RolePermission(Enum):
    ROLE_NEW = "role_new"
    ROLE_DOWN = "role_down"
    ROLE_UP = "role_up"
    ROLE_MOD = "role_mod"
