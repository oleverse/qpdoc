"""Add new tables or modify existing ones

Revision ID: 0d66ec5623c3
Revises: 5fa5e6050b8f
Create Date: 2023-11-16 22:27:18.538272

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d66ec5623c3'
down_revision: Union[str, None] = '5fa5e6050b8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
