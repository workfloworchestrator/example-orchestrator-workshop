"""node and circuit initial workflows.

Revision ID: 007a889a7c71
Revises: aa9d987fc4f3
Create Date: 2023-09-28 14:07:19.183478

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '007a889a7c71'
down_revision = 'aa9d987fc4f3'
branch_labels = None
depends_on = None


from orchestrator.migrations.helpers import create_workflow, delete_workflow

new_workflows = [
    {
        "name": "create_node",
        "target": "CREATE",
        "description": "Create Node",
        "product_type": "Node"
    },
    {
        "name": "create_circuit",
        "target": "CREATE",
        "description": "Create Circuit",
        "product_type": "Circuit"
    },
    {
        "name": "modify_circuit",
        "target": "MODIFY",
        "description": "Modify the circuit maintenance state",
        "product_type": "Circuit"
    },
    {
        "name": "terminate_circuit",
        "target": "TERMINATE",
        "description": "Terminate the circuit",
        "product_type": "Circuit"
    }
]


def upgrade() -> None:
    conn = op.get_bind()
    for workflow in new_workflows:
        create_workflow(conn, workflow)


def downgrade() -> None:
    conn = op.get_bind()
    for workflow in new_workflows:
        delete_workflow(conn, workflow["name"])
