"""empty message

Revision ID: 2ff33112b113
Revises: None
Create Date: 2015-09-27 11:17:07.153041

"""

# revision identifiers, used by Alembic.
revision = '2ff33112b113'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('author_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'posts', 'users', ['author_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'posts', type_='foreignkey')
    op.drop_column('posts', 'author_id')
    ### end Alembic commands ###
