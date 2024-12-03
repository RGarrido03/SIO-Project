"""Add new organization role table

Revision ID: c959e775735e
Revises: a0f82689c5d4
Create Date: 2024-12-03 01:50:09.112560

"""

from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "c959e775735e"
down_revision: Union[str, None] = "a0f82689c5d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "organizationrole",
        sa.Column(
            "organization_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
        sa.Column("role", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column(
            "permissions",
            postgresql.ARRAY(
                sa.Enum(
                    "DOC_ACL",
                    "DOC_READ",
                    "DOC_DELETE",
                    "ROLE_ACL",
                    "SUBJECT_NEW",
                    "SUBJECT_DOWN",
                    "SUBJECT_UP",
                    "DOC_NEW",
                    "ROLE_NEW",
                    "ROLE_DOWN",
                    "ROLE_UP",
                    "ROLE_MOD",
                )
            ),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["organization_name"],
            ["organization.name"],
        ),
        sa.PrimaryKeyConstraint("organization_name", "role"),
    )
    op.create_index(
        op.f("ix_organizationrole_role"), "organizationrole", ["role"], unique=False
    )
    op.add_column(
        "subjectorganizationlink",
        sa.Column("role_ids", sa.ARRAY(sa.String()), nullable=True),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("subjectorganizationlink", "role_ids")
    op.drop_index(op.f("ix_organizationrole_role"), table_name="organizationrole")
    op.drop_table("organizationrole")
    # ### end Alembic commands ###
