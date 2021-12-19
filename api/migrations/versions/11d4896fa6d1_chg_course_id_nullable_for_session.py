"""CHG course_id nullable for session

Revision ID: 11d4896fa6d1
Revises: f201544d8948
Create Date: 2021-12-18 21:01:07.519890

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "11d4896fa6d1"
down_revision = "f201544d8948"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "theia_session",
        "course_id",
        existing_type=mysql.VARCHAR(length=128),
        nullable=True,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "theia_session",
        "course_id",
        existing_type=mysql.VARCHAR(length=128),
        nullable=False,
    )
    # ### end Alembic commands ###