"""Initial migrations

Revision ID: 92f8ac5bf33f
Revises: 
Create Date: 2024-10-28 15:45:42.716186

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "92f8ac5bf33f"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Organization
    op.create_table(
        "organization",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("name"),
    )
    op.create_index(
        op.f("ix_organization_name"), "organization", ["name"], unique=False
    )

    # Role
    op.create_table(
        "role",
        sa.Column("name", sa.Enum("MANAGERS", "USER", name="roleenum"), nullable=False),
        sa.Column(
            "role_permissions",
            postgresql.ARRAY(
                sa.Enum(
                    "ROLE_NEW",
                    "ROLE_DOWN",
                    "ROLE_UP",
                    "ROLE_MOD",
                    name="rolepermission",
                )
            ),
            nullable=True,
        ),
        sa.Column(
            "organization_permissions",
            postgresql.ARRAY(
                sa.Enum(
                    "ROLE_ACL",
                    "SUBJECT_NEW",
                    "SUBJECT_DOWN",
                    "SUBJECT_UP",
                    "DOC_NEW",
                    name="organizationpermission",
                )
            ),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("name"),
    )
    op.create_index(op.f("ix_role_name"), "role", ["name"], unique=False)

    # Subject
    op.create_table(
        "subject",
        sa.Column("username", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("full_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("password", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint("username"),
    )
    op.create_index(op.f("ix_subject_email"), "subject", ["email"], unique=False)
    op.create_index(op.f("ix_subject_username"), "subject", ["username"], unique=False)

    # Public Key
    op.create_table(
        "publickey",
        sa.Column("key", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "subject_username", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["subject_username"],
            ["subject.username"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_publickey_key"), "publickey", ["key"], unique=False)

    # Subject - Role
    op.create_table(
        "subjectrolelink",
        sa.Column(
            "subject_username", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column(
            "role_name", sa.Enum("MANAGERS", "USER", name="roleenum"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["role_name"],
            ["role.name"],
        ),
        sa.ForeignKeyConstraint(
            ["subject_username"],
            ["subject.username"],
        ),
        sa.PrimaryKeyConstraint("subject_username", "role_name"),
    )

    # Subject - Organization
    op.create_table(
        "subjectorganizationlink",
        sa.Column(
            "subject_username", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column(
            "organization_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("public_key", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_name"],
            ["organization.name"],
        ),
        sa.ForeignKeyConstraint(
            ["public_key"],
            ["publickey.id"],
        ),
        sa.ForeignKeyConstraint(
            ["subject_username"],
            ["subject.username"],
        ),
        sa.PrimaryKeyConstraint("subject_username", "organization_name"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("subjectorganizationlink")
    op.drop_table("subjectrolelink")
    op.drop_index(op.f("ix_publickey_key"), table_name="publickey")
    op.drop_table("publickey")
    op.drop_index(op.f("ix_subject_username"), table_name="subject")
    op.drop_index(op.f("ix_subject_email"), table_name="subject")
    op.drop_table("subject")
    op.drop_index(op.f("ix_role_name"), table_name="role")
    op.drop_table("role")
    op.drop_index(op.f("ix_organization_name"), table_name="organization")
    op.drop_table("organization")
    # ### end Alembic commands ###
