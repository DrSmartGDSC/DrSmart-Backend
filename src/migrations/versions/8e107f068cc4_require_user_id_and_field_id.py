"""require user_id and field_id

Revision ID: 8e107f068cc4
Revises: 3d0102485013
Create Date: 2022-03-17 23:59:23.178787

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e107f068cc4'
down_revision = '3d0102485013'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('posts', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('posts', 'field_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('posts', 'field_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('posts', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
