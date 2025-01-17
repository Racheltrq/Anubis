"""CHG assignment repo netid tracking

Revision ID: 28971042fc9c
Revises: 7a2f58a7654f
Create Date: 2022-01-15 18:21:07.682465

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "28971042fc9c"
down_revision = "7a2f58a7654f"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "assignment_repo",
        sa.Column("netid", sa.String(length=128), nullable=True),
    )

    conn = op.get_bind()
    with conn.begin():
        conn.execute('update assignment_repo '
                     'join user on assignment_repo.owner_id = user.id '
                     'set assignment_repo.netid = user.netid;')

    op.alter_column(
        "assignment_repo",
        "netid",
        existing_type=mysql.VARCHAR(collation="utf8mb4_unicode_ci", length=128),
        nullable=False,
    )

    op.drop_column("assignment_repo", "github_username")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "assignment_repo",
        sa.Column("github_username", mysql.MEDIUMTEXT(), nullable=False),
    )
    op.drop_column("assignment_repo", "netid")
    # ### end Alembic commands ###
