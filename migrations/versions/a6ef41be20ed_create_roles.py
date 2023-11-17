"""create roles

Revision ID: a6ef41be20ed
Revises: 4f3aaa5d5551
Create Date: 2023-11-17 17:06:40.336583

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from app.database.models import RoleNames


# revision identifiers, used by Alembic.
revision: str = 'a6ef41be20ed'
down_revision: Union[str, None] = '4f3aaa5d5551'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    roles_table = table(
        "roles",
        column("name", sa.String),
    )
    op.bulk_insert(
        roles_table,
        [
            {"name": f"{RoleNames.admin.name}"},
            {"name": f"{RoleNames.moderator.name}"},
            {"name": f"{RoleNames.user.name}"}
        ]
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###