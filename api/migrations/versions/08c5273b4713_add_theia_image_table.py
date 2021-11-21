"""ADD theia_image table

Revision ID: 08c5273b4713
Revises: 18b5fce3df50
Create Date: 2021-11-20 21:37:38.639910

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from hashlib import sha512
import os

# revision identifiers, used by Alembic.
revision = "08c5273b4713"
down_revision = "18b5fce3df50"
branch_labels = None
depends_on = None


def get_id():
    return sha512(os.urandom(32)).hexdigest()[:32]


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    conn = op.get_bind()
    with conn.begin():
        theia_image_table = op.create_table(
            "theia_image",
            sa.Column("id", sa.String(length=128), nullable=False),
            sa.Column("image", sa.String(length=1024), nullable=False),
            sa.Column("label", sa.String(length=1024), nullable=False),
            sa.Column("public", sa.Boolean(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

        images = conn.execute(sa.text('select distinct image from theia_session;'))
        images = [i[0] for i in images]
        images = [
            {
                'id': get_id(),
                'image': i,
                'label': i,
                'public': 0,
            }
            for i in images
        ]
        op.bulk_insert(theia_image_table, images)

        # Handle assignment table
        op.add_column(
            "assignment",
            sa.Column("theia_image_id", sa.String(length=128), nullable=True),
        )
        op.create_foreign_key(
            None, "assignment", "theia_image", ["theia_image_id"], ["id"]
        )
        for i in images:
            conn.execute(
                sa.text('update assignment set theia_image_id = :id where theia_image = :image;'),
                id=i['id'], image=i['image'],
            )
        op.drop_column("assignment", "theia_image")

        # Handle theia_session table
        op.add_column(
            "theia_session",
            sa.Column("image_id", sa.String(length=128), nullable=True),
        )
        for i in images:
            conn.execute(
                sa.text('update theia_session set image_id = :id where image = :image;'),
                id=i['id'], image=i['image'],
            )
        op.drop_column("theia_session", "image")
        op.create_foreign_key(
            None, "theia_session", "theia_image", ["image_id"], ["id"]
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "theia_session",
        sa.Column(
            "image",
            mysql.VARCHAR(collation="utf8mb4_unicode_ci", length=128),
            nullable=True,
        ),
    )
    op.drop_constraint(None, "theia_session", type_="foreignkey")
    op.drop_column("theia_session", "image_id")
    op.drop_constraint(None, "assignment", type_="foreignkey")
    op.drop_table("theia_image")
    # ### end Alembic commands ###
