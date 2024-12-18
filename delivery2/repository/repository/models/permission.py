from enum import Enum


class Permission(str, Enum):
    ROLE_ACL = "ROLE_ACL"
    SUBJECT_NEW = "SUBJECT_NEW"
    SUBJECT_DOWN = "SUBJECT_DOWN"
    SUBJECT_UP = "SUBJECT_UP"
    DOC_NEW = "DOC_NEW"
    ROLE_NEW = "ROLE_NEW"
    ROLE_DOWN = "ROLE_DOWN"
    ROLE_UP = "ROLE_UP"
    ROLE_MOD = "ROLE_MOD"


class DocumentPermission(str, Enum):
    DOC_ACL = "DOC_ACL"
    DOC_READ = "DOC_READ"
    DOC_DELETE = "DOC_DELETE"


all_permissions = [perm for perm in Permission]
