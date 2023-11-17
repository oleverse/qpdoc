"""Add new tables or modify existing ones

Revision ID: e03da8ef70b2
Revises: 934b6d78c9b9
Create Date: 2023-11-17 05:49:58.490860

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e03da8ef70b2'
down_revision: Union[str, None] = '934b6d78c9b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_files_id', table_name='files')
    op.drop_table('files')
    op.add_column('pdfs', sa.Column('owner_id', sa.Integer(), nullable=True))
    op.drop_constraint('pdfs_user_id_fkey', 'pdfs', type_='foreignkey')
    op.create_foreign_key(None, 'pdfs', 'users', ['owner_id'], ['id'])
    op.drop_column('pdfs', 'user_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pdfs', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'pdfs', type_='foreignkey')
    op.create_foreign_key('pdfs_user_id_fkey', 'pdfs', 'users', ['user_id'], ['id'])
    op.drop_column('pdfs', 'owner_id')
    op.create_table('files',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('filename', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('owner_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name='files_owner_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='files_pkey')
    )
    op.create_index('ix_files_id', 'files', ['id'], unique=False)
    # ### end Alembic commands ###