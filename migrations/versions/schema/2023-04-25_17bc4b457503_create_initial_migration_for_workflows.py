"""Create initial migration for workflows.

Revision ID: 17bc4b457503
Revises: 2136d6098238
Create Date: 2023-04-25 14:48:16.185913

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '17bc4b457503'
down_revision = '2136d6098238'
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
