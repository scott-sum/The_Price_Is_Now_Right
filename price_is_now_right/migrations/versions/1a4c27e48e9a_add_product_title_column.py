"""add product title column

Revision ID: 1a4c27e48e9a
Revises: 11eb9759f228
Create Date: 2020-09-02 10:33:39.476407

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a4c27e48e9a'
down_revision = '11eb9759f228'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('product')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('product',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('userId', sa.INTEGER(), nullable=False),
    sa.Column('productURL', sa.VARCHAR(), nullable=False),
    sa.Column('currentPrice', sa.INTEGER(), nullable=True),
    sa.Column('userBudget', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['userId'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
