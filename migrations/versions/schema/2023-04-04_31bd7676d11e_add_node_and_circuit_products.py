"""Add node and circuit products.

Revision ID: 31bd7676d11e
Revises:
Create Date: 2023-04-04 09:56:24.462898

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '31bd7676d11e'
down_revision = None
branch_labels = ('data',)
depends_on = 'e05bb1967eff'


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute("""
INSERT INTO products (name, description, product_type, tag, status) VALUES ('Node', 'Node product', 'Node', 'node', 'active') RETURNING products.product_id
    """)
    conn.execute("""
INSERT INTO products (name, description, product_type, tag, status) VALUES ('Circuit', 'Circuit product', 'Circuit', 'circuit', 'active') RETURNING products.product_id
    """)
    conn.execute("""
INSERT INTO fixed_inputs (name, value, product_id) VALUES ('speed', '100G', (SELECT products.product_id FROM products WHERE products.name IN ('Circuit')))
    """)
    conn.execute("""
INSERT INTO product_blocks (name, description, tag, status) VALUES ('Node', 'node block', 'node', 'active') RETURNING product_blocks.product_block_id
    """)
    conn.execute("""
INSERT INTO product_blocks (name, description, tag, status) VALUES ('Circuit', 'circuit block', 'circuit', 'active') RETURNING product_blocks.product_block_id
    """)
    conn.execute("""
INSERT INTO product_blocks (name, description, tag, status) VALUES ('Layer 3 Interface', 'layer 3 interface block', 'l3iface', 'active') RETURNING product_blocks.product_block_id
    """)
    conn.execute("""
INSERT INTO product_blocks (name, description, tag, status) VALUES ('Port', 'port block', 'port', 'active') RETURNING product_blocks.product_block_id
    """)
    conn.execute("""
INSERT INTO resource_types (resource_type, description) VALUES ('port_id', 'port ID') RETURNING resource_types.resource_type_id
    """)
    conn.execute("""
INSERT INTO resource_types (resource_type, description) VALUES ('node_name', 'name of the node') RETURNING resource_types.resource_type_id
    """)
    conn.execute("""
INSERT INTO resource_types (resource_type, description) VALUES ('ipv4_loopback', 'v4 loopback address') RETURNING resource_types.resource_type_id
    """)
    conn.execute("""
INSERT INTO resource_types (resource_type, description) VALUES ('ipv6_loopback', 'v6 loopback address') RETURNING resource_types.resource_type_id
    """)
    conn.execute("""
INSERT INTO resource_types (resource_type, description) VALUES ('under_maintenance', 'boolean to indicate of this circuit is under maintenance') RETURNING resource_types.resource_type_id
    """)
    conn.execute("""
INSERT INTO resource_types (resource_type, description) VALUES ('circuit_id', 'circuit ID') RETURNING resource_types.resource_type_id
    """)
    conn.execute("""
INSERT INTO resource_types (resource_type, description) VALUES ('node_id', 'node ID') RETURNING resource_types.resource_type_id
    """)
    conn.execute("""
INSERT INTO resource_types (resource_type, description) VALUES ('v6_ip_address', 'v6 address') RETURNING resource_types.resource_type_id
    """)
    conn.execute("""
INSERT INTO resource_types (resource_type, description) VALUES ('port_description', 'port description') RETURNING resource_types.resource_type_id
    """)
    conn.execute("""
INSERT INTO product_product_blocks (product_id, product_block_id) VALUES ((SELECT products.product_id FROM products WHERE products.name IN ('Node')), (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Node')))
    """)
    conn.execute("""
INSERT INTO product_product_blocks (product_id, product_block_id) VALUES ((SELECT products.product_id FROM products WHERE products.name IN ('Circuit')), (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Circuit')))
    """)
    conn.execute("""
INSERT INTO product_block_relations (in_use_by_id, depends_on_id) VALUES ((SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Circuit')), (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Layer 3 Interface')))
    """)
    conn.execute("""
INSERT INTO product_block_relations (in_use_by_id, depends_on_id) VALUES ((SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Layer 3 Interface')), (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Port')))
    """)
    conn.execute("""
INSERT INTO product_block_relations (in_use_by_id, depends_on_id) VALUES ((SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Port')), (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Node')))
    """)
    conn.execute("""
INSERT INTO product_block_resource_types (product_block_id, resource_type_id) VALUES ((SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Node')), (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('node_id')))
    """)
    conn.execute("""
INSERT INTO product_block_resource_types (product_block_id, resource_type_id) VALUES ((SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Node')), (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('node_name')))
    """)
    conn.execute("""
INSERT INTO product_block_resource_types (product_block_id, resource_type_id) VALUES ((SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Node')), (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('ipv4_loopback')))
    """)
    conn.execute("""
INSERT INTO product_block_resource_types (product_block_id, resource_type_id) VALUES ((SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Node')), (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('ipv6_loopback')))
    """)
    conn.execute("""
INSERT INTO product_block_resource_types (product_block_id, resource_type_id) VALUES ((SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Circuit')), (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('circuit_id')))
    """)
    conn.execute("""
INSERT INTO product_block_resource_types (product_block_id, resource_type_id) VALUES ((SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Circuit')), (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('under_maintenance')))
    """)
    conn.execute("""
INSERT INTO product_block_resource_types (product_block_id, resource_type_id) VALUES ((SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Layer 3 Interface')), (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('v6_ip_address')))
    """)
    conn.execute("""
INSERT INTO product_block_resource_types (product_block_id, resource_type_id) VALUES ((SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Port')), (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('port_id')))
    """)
    conn.execute("""
INSERT INTO product_block_resource_types (product_block_id, resource_type_id) VALUES ((SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Port')), (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('port_description')))
    """)


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute("""
DELETE FROM product_block_resource_types WHERE product_block_resource_types.product_block_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Node')) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('node_id'))
    """)
    conn.execute("""
DELETE FROM subscription_instance_values USING product_block_resource_types WHERE subscription_instance_values.subscription_instance_id IN (SELECT subscription_instances.subscription_instance_id FROM subscription_instances WHERE subscription_instances.subscription_instance_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Node'))) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('node_id'))
    """)
    conn.execute("""
DELETE FROM product_block_resource_types WHERE product_block_resource_types.product_block_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Node')) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('node_name'))
    """)
    conn.execute("""
DELETE FROM subscription_instance_values USING product_block_resource_types WHERE subscription_instance_values.subscription_instance_id IN (SELECT subscription_instances.subscription_instance_id FROM subscription_instances WHERE subscription_instances.subscription_instance_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Node'))) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('node_name'))
    """)
    conn.execute("""
DELETE FROM product_block_resource_types WHERE product_block_resource_types.product_block_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Node')) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('ipv4_loopback'))
    """)
    conn.execute("""
DELETE FROM subscription_instance_values USING product_block_resource_types WHERE subscription_instance_values.subscription_instance_id IN (SELECT subscription_instances.subscription_instance_id FROM subscription_instances WHERE subscription_instances.subscription_instance_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Node'))) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('ipv4_loopback'))
    """)
    conn.execute("""
DELETE FROM product_block_resource_types WHERE product_block_resource_types.product_block_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Node')) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('ipv6_loopback'))
    """)
    conn.execute("""
DELETE FROM subscription_instance_values USING product_block_resource_types WHERE subscription_instance_values.subscription_instance_id IN (SELECT subscription_instances.subscription_instance_id FROM subscription_instances WHERE subscription_instances.subscription_instance_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Node'))) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('ipv6_loopback'))
    """)
    conn.execute("""
DELETE FROM product_block_resource_types WHERE product_block_resource_types.product_block_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Circuit')) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('circuit_id'))
    """)
    conn.execute("""
DELETE FROM subscription_instance_values USING product_block_resource_types WHERE subscription_instance_values.subscription_instance_id IN (SELECT subscription_instances.subscription_instance_id FROM subscription_instances WHERE subscription_instances.subscription_instance_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Circuit'))) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('circuit_id'))
    """)
    conn.execute("""
DELETE FROM product_block_resource_types WHERE product_block_resource_types.product_block_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Circuit')) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('under_maintenance'))
    """)
    conn.execute("""
DELETE FROM subscription_instance_values USING product_block_resource_types WHERE subscription_instance_values.subscription_instance_id IN (SELECT subscription_instances.subscription_instance_id FROM subscription_instances WHERE subscription_instances.subscription_instance_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Circuit'))) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('under_maintenance'))
    """)
    conn.execute("""
DELETE FROM product_block_resource_types WHERE product_block_resource_types.product_block_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Layer 3 Interface')) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('v6_ip_address'))
    """)
    conn.execute("""
DELETE FROM subscription_instance_values USING product_block_resource_types WHERE subscription_instance_values.subscription_instance_id IN (SELECT subscription_instances.subscription_instance_id FROM subscription_instances WHERE subscription_instances.subscription_instance_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Layer 3 Interface'))) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('v6_ip_address'))
    """)
    conn.execute("""
DELETE FROM product_block_resource_types WHERE product_block_resource_types.product_block_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Port')) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('port_id'))
    """)
    conn.execute("""
DELETE FROM subscription_instance_values USING product_block_resource_types WHERE subscription_instance_values.subscription_instance_id IN (SELECT subscription_instances.subscription_instance_id FROM subscription_instances WHERE subscription_instances.subscription_instance_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Port'))) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('port_id'))
    """)
    conn.execute("""
DELETE FROM product_block_resource_types WHERE product_block_resource_types.product_block_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Port')) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('port_description'))
    """)
    conn.execute("""
DELETE FROM subscription_instance_values USING product_block_resource_types WHERE subscription_instance_values.subscription_instance_id IN (SELECT subscription_instances.subscription_instance_id FROM subscription_instances WHERE subscription_instances.subscription_instance_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Port'))) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('port_description'))
    """)
    conn.execute("""
DELETE FROM subscription_instance_values WHERE subscription_instance_values.resource_type_id IN (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('port_id', 'node_name', 'ipv4_loopback', 'ipv6_loopback', 'under_maintenance', 'circuit_id', 'node_id', 'v6_ip_address', 'port_description'))
    """)
    conn.execute("""
DELETE FROM resource_types WHERE resource_types.resource_type IN ('port_id', 'node_name', 'ipv4_loopback', 'ipv6_loopback', 'under_maintenance', 'circuit_id', 'node_id', 'v6_ip_address', 'port_description')
    """)
    conn.execute("""
DELETE FROM product_product_blocks WHERE product_product_blocks.product_id IN (SELECT products.product_id FROM products WHERE products.name IN ('Node')) AND product_product_blocks.product_block_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Node'))
    """)
    conn.execute("""
DELETE FROM product_product_blocks WHERE product_product_blocks.product_id IN (SELECT products.product_id FROM products WHERE products.name IN ('Circuit')) AND product_product_blocks.product_block_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Circuit'))
    """)
    conn.execute("""
DELETE FROM product_block_relations WHERE product_block_relations.in_use_by_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Circuit')) AND product_block_relations.depends_on_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Layer 3 Interface'))
    """)
    conn.execute("""
DELETE FROM product_block_relations WHERE product_block_relations.in_use_by_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Layer 3 Interface')) AND product_block_relations.depends_on_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Port'))
    """)
    conn.execute("""
DELETE FROM product_block_relations WHERE product_block_relations.in_use_by_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Port')) AND product_block_relations.depends_on_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Node'))
    """)
    conn.execute("""
DELETE FROM fixed_inputs WHERE fixed_inputs.product_id IN (SELECT products.product_id FROM products WHERE products.name IN ('Circuit')) AND fixed_inputs.name = 'speed'
    """)
    conn.execute("""
DELETE FROM subscription_instances WHERE subscription_instances.product_block_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Port', 'Layer 3 Interface', 'Circuit', 'Node'))
    """)
    conn.execute("""
DELETE FROM product_blocks WHERE product_blocks.name IN ('Port', 'Layer 3 Interface', 'Circuit', 'Node')
    """)
    conn.execute("""
DELETE FROM processes WHERE processes.pid IN (SELECT processes_subscriptions.pid FROM processes_subscriptions WHERE processes_subscriptions.subscription_id IN (SELECT subscriptions.subscription_id FROM subscriptions WHERE subscriptions.product_id IN (SELECT products.product_id FROM products WHERE products.name IN ('Circuit', 'Node'))))
    """)
    conn.execute("""
DELETE FROM processes_subscriptions WHERE processes_subscriptions.subscription_id IN (SELECT subscriptions.subscription_id FROM subscriptions WHERE subscriptions.product_id IN (SELECT products.product_id FROM products WHERE products.name IN ('Circuit', 'Node')))
    """)
    conn.execute("""
DELETE FROM subscription_instances WHERE subscription_instances.subscription_id IN (SELECT subscriptions.subscription_id FROM subscriptions WHERE subscriptions.product_id IN (SELECT products.product_id FROM products WHERE products.name IN ('Circuit', 'Node')))
    """)
    conn.execute("""
DELETE FROM subscriptions WHERE subscriptions.product_id IN (SELECT products.product_id FROM products WHERE products.name IN ('Circuit', 'Node'))
    """)
    conn.execute("""
DELETE FROM products WHERE products.name IN ('Circuit', 'Node')
    """)
