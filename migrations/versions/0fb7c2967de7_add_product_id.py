"""add product id

Revision ID: 0fb7c2967de7
Revises: 5de85c6a7295
Create Date: 2020-09-01 17:42:30.493257

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0fb7c2967de7'
down_revision = '5de85c6a7295'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("product") as batch_op:
        batch_op.alter_column('userId',
                existing_type=sa.INTEGER(),
                nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("product") as batch_op:
        batch_op.alter_column('userId',
                existing_type=sa.INTEGER(),
                nullable=False)
    # ### end Alembic commands ###
