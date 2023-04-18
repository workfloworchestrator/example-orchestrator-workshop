"""Add Circuit Workflows.

Revision ID: e93d0e2acaa7
Revises: ebd8f3b36312
Create Date: 2023-04-18 11:55:00.726399

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'e93d0e2acaa7'
down_revision = 'ebd8f3b36312'
branch_labels = None
depends_on = None


from orchestrator.migrations.helpers import create_workflow, delete_workflow

new_workflows = [
    {
        "name": "create_circuit",
        "target": "CREATE",
        "description": "Create Node",
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
