"""empty message

Revision ID: 19e766bd21a9
Revises: 17d7444ca6fe
Create Date: 2019-05-16 13:33:40.323663

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19e766bd21a9'
down_revision = '17d7444ca6fe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('device',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('member_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=30), nullable=True),
    sa.Column('sn', sa.String(length=32), nullable=True),
    sa.Column('type', sa.String(length=20), nullable=True),
    sa.Column('img', sa.String(length=200), nullable=True),
    sa.Column('position', sa.String(length=200), nullable=True),
    sa.Column('online', sa.Integer(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('sub', sa.String(length=50), nullable=True),
    sa.Column('pub', sa.String(length=50), nullable=True),
    sa.Column('updated_time', sa.DateTime(), nullable=True),
    sa.Column('created_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('device_time',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('device_id', sa.Integer(), nullable=True),
    sa.Column('type', sa.Integer(), nullable=True),
    sa.Column('customize', sa.String(length=30), nullable=True),
    sa.Column('open_time', sa.DateTime(), nullable=True),
    sa.Column('close_time', sa.DateTime(), nullable=True),
    sa.Column('updated_time', sa.DateTime(), nullable=True),
    sa.Column('created_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('device_time')
    op.drop_table('device')
    # ### end Alembic commands ###