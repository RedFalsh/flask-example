"""empty message

Revision ID: f39519f309d3
Revises: 19e766bd21a9
Create Date: 2019-05-16 17:05:07.008687

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f39519f309d3'
down_revision = '19e766bd21a9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('device_mqtt',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('device_id', sa.Integer(), nullable=True),
    sa.Column('server', sa.String(length=100), nullable=True),
    sa.Column('port', sa.Integer(), nullable=True),
    sa.Column('login_user', sa.String(length=20), nullable=True),
    sa.Column('login_pwd', sa.String(length=30), nullable=True),
    sa.Column('sub', sa.String(length=50), nullable=True),
    sa.Column('pub', sa.String(length=50), nullable=True),
    sa.Column('updated_time', sa.DateTime(), nullable=True),
    sa.Column('created_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('device_mqtt')
    # ### end Alembic commands ###
