"""added cascade deletes

Revision ID: 85d4e5e84ff2
Revises: 87cdceaa52cc
Create Date: 2023-08-21 21:05:52.077380

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85d4e5e84ff2'
down_revision: Union[str, None] = '87cdceaa52cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_chemicals_id', table_name='chemicals')
    op.drop_table('chemicals')
    op.drop_index('ix_locations_id', table_name='locations')
    op.drop_table('locations')
    op.drop_index('ix_profiles_id', table_name='profiles')
    op.drop_table('profiles')
    op.drop_index('ix_orders_id', table_name='orders')
    op.drop_table('orders')
    op.drop_index('ix_suppliers_id', table_name='suppliers')
    op.drop_table('suppliers')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('suppliers',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('supplierName', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_suppliers_id', 'suppliers', ['id'], unique=False)
    op.create_table('orders',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('chemical_id', sa.INTEGER(), nullable=True),
    sa.Column('supplier_id', sa.INTEGER(), nullable=True),
    sa.Column('location_id', sa.INTEGER(), nullable=True),
    sa.Column('status', sa.VARCHAR(length=9), nullable=True),
    sa.Column('amount', sa.INTEGER(), nullable=True),
    sa.Column('amountUnit', sa.VARCHAR(length=2), nullable=True),
    sa.Column('isConsumed', sa.BOOLEAN(), nullable=True),
    sa.Column('orderDate', sa.DATETIME(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('supplierPN', sa.VARCHAR(), nullable=True),
    sa.ForeignKeyConstraint(['chemical_id'], ['chemicals.id'], ),
    sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
    sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_orders_id', 'orders', ['id'], unique=False)
    op.create_table('profiles',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('username', sa.VARCHAR(), nullable=True),
    sa.Column('full_name', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_index('ix_profiles_id', 'profiles', ['id'], unique=False)
    op.create_table('locations',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('locationName', sa.VARCHAR(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['profiles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_locations_id', 'locations', ['id'], unique=False)
    op.create_table('chemicals',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('CAS', sa.VARCHAR(), nullable=True),
    sa.Column('chemicalName', sa.VARCHAR(), nullable=True),
    sa.Column('MW', sa.VARCHAR(), nullable=True),
    sa.Column('MP', sa.VARCHAR(), nullable=True),
    sa.Column('BP', sa.VARCHAR(), nullable=True),
    sa.Column('density', sa.VARCHAR(), nullable=True),
    sa.Column('smile', sa.VARCHAR(), nullable=True),
    sa.Column('inchi', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('CAS')
    )
    op.create_index('ix_chemicals_id', 'chemicals', ['id'], unique=False)
    # ### end Alembic commands ###
