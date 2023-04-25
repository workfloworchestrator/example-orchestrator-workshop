"""Add New Port Name Field for convenience of config rendering.

Revision ID: a3c1cf2ac792
Revises: e93d0e2acaa7
Create Date: 2023-04-25 11:36:32.261126

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'a3c1cf2ac792'
down_revision = 'e93d0e2acaa7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute("""
INSERT INTO resource_types (resource_type, description) VALUES ('port_name', 'Port Name') RETURNING resource_types.resource_type_id
    """)
    conn.execute("""
INSERT INTO product_block_resource_types (product_block_id, resource_type_id) VALUES ((SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Port')), (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('port_name')))
    """)


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute("""
DELETE FROM product_block_resource_types WHERE product_block_resource_types.product_block_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Port')) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('port_name'))
    """)
    conn.execute("""
DELETE FROM subscription_instance_values USING product_block_resource_types WHERE subscription_instance_values.subscription_instance_id IN (SELECT subscription_instances.subscription_instance_id FROM subscription_instances WHERE subscription_instances.subscription_instance_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Port'))) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('port_name'))
    """)
    conn.execute("""
DELETE FROM subscription_instance_values WHERE subscription_instance_values.resource_type_id IN (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('port_name'))
    """)
    conn.execute("""
DELETE FROM resource_types WHERE resource_types.resource_type IN ('port_name')
    """)
