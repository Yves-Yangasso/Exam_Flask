"""empty message

Revision ID: 866d89ea99fb
Revises: c5f636129c29
Create Date: 2024-06-19 17:33:06.123943

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '866d89ea99fb'
down_revision = 'c5f636129c29'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('emprunt',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_user', sa.Integer(), nullable=False),
    sa.Column('id_livre', sa.Integer(), nullable=False),
    sa.Column('dure', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id_livre'], ['livre.id'], ),
    sa.ForeignKeyConstraint(['id_user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('emprunt')
    # ### end Alembic commands ###
