"""Initial domain model migration.

Revision ID: 2136d6098238
Revises:
Create Date: 2023-04-25 14:44:12.697238

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '2136d6098238'
down_revision = None
branch_labels = ('data',)
depends_on = 'e05bb1967eff'


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute("""
INSERT INTO products (name, description, product_type, tag, status) VALUES ('Node', 'Node', 'Node', 'Node', 'active') RETURNING products.product_id
    """)
    conn.execute("""
INSERT INTO products (name, description, product_type, tag, status) VALUES ('Circuit', 'Circuit', 'Circuit', 'Circuit', 'active') RETURNING products.product_id
    """)
    conn.execute("""
INSERT INTO fixed_inputs (name, value, product_id) VALUES ('speed', '100G', (SELECT products.product_id FROM products WHERE products.name IN ('Circuit')))
    """)
    conn.execute("""
INSERT INTO product_blocks (name, description, tag, status) VALUES ('Node', 'Node', 'Node', 'active') RETURNING product_blocks.product_block_id
    """)
    conn.execute("""
INSERT INTO product_blocks (name, description, tag, status) VALUES ('Circuit', 'Circuit', 'Circuit', 'active') RETURNING product_blocks.product_block_id
    """)
    conn.execute("""
INSERT INTO product_blocks (name, description, tag, status) VALUES ('Layer 3 Interface', 'Layer 3 Interface', 'Layer 3 Interface', 'active') RETURNING product_blocks.product_block_id
    """)
    conn.execute("""
INSERT INTO product_blocks (name, description, tag, status) VALUES ('Port', 'Port', 'Port', 'active') RETURNING product_blocks.product_block_id
    """)
    conn.execute("""
INSERT INTO resource_types (resource_type, description) VALUES ('ipv4_loopback', 'IPv4 Loopback') RETURNING resource_types.resource_type_id
    """)
    conn.execute("""
INSERT INTO resource_types (resource_type, description) VALUES ('under_maintenance', 'Under Maintenance') RETURNING resource_types.resource_type_id
    """)
    conn.execute("""
INSERT INTO resource_types (resource_type, description) VALUES ('port_name', 'Port Name') RETURNING resource_types.resource_type_id
    """)
    conn.execute("""
INSERT INTO resource_types (resource_type, description) VALUES ('node_id', 'Node ID') RETURNING resource_types.resource_type_id
    """)
    conn.execute("""
INSERT INTO resource_types (resource_type, description) VALUES ('port_id', 'Port ID') RETURNING resource_types.resource_type_id
    """)
    conn.execute("""
INSERT INTO resource_types (resource_type, description) VALUES ('port_description', 'Port ID') RETURNING resource_types.resource_type_id
    """)
    conn.execute("""
INSERT INTO resource_types (resource_type, description) VALUES ('ipv6_loopback', 'IPv6 Loopback') RETURNING resource_types.resource_type_id
    """)
    conn.execute("""
INSERT INTO resource_types (resource_type, description) VALUES ('v6_ip_address', 'IPv6 IP Address') RETURNING resource_types.resource_type_id
    """)
    conn.execute("""
INSERT INTO resource_types (resource_type, description) VALUES ('node_name', 'Node Name') RETURNING resource_types.resource_type_id
    """)
    conn.execute("""
INSERT INTO resource_types (resource_type, description) VALUES ('circuit_id', 'Circuit ID') RETURNING resource_types.resource_type_id
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
    conn.execute("""
INSERT INTO product_block_resource_types (product_block_id, resource_type_id) VALUES ((SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Port')), (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('port_name')))
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
DELETE FROM product_block_resource_types WHERE product_block_resource_types.product_block_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Port')) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('port_name'))
    """)
    conn.execute("""
DELETE FROM subscription_instance_values USING product_block_resource_types WHERE subscription_instance_values.subscription_instance_id IN (SELECT subscription_instances.subscription_instance_id FROM subscription_instances WHERE subscription_instances.subscription_instance_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Port'))) AND product_block_resource_types.resource_type_id = (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('port_name'))
    """)
    conn.execute("""
DELETE FROM subscription_instance_values WHERE subscription_instance_values.resource_type_id IN (SELECT resource_types.resource_type_id FROM resource_types WHERE resource_types.resource_type IN ('ipv4_loopback', 'under_maintenance', 'port_name', 'node_id', 'port_id', 'port_description', 'ipv6_loopback', 'v6_ip_address', 'node_name', 'circuit_id'))
    """)
    conn.execute("""
DELETE FROM resource_types WHERE resource_types.resource_type IN ('ipv4_loopback', 'under_maintenance', 'port_name', 'node_id', 'port_id', 'port_description', 'ipv6_loopback', 'v6_ip_address', 'node_name', 'circuit_id')
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
DELETE FROM subscription_instances WHERE subscription_instances.product_block_id IN (SELECT product_blocks.product_block_id FROM product_blocks WHERE product_blocks.name IN ('Circuit', 'Port', 'Node', 'Layer 3 Interface'))
    """)
    conn.execute("""
DELETE FROM product_blocks WHERE product_blocks.name IN ('Circuit', 'Port', 'Node', 'Layer 3 Interface')
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
