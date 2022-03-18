"""empty message

Revision ID: a4688c969931
Revises: 8e107f068cc4
Create Date: 2022-03-18 02:24:49.924673

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4688c969931'
down_revision = '8e107f068cc4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('answered', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'answered')
    # ### end Alembic commands ###
