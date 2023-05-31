"""Add modify and terminate workflows.

Revision ID: 6b554ed41b13
Revises: 17bc4b457503
Create Date: 2023-05-31 16:08:16.185913

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '6b554ed41b13'
down_revision = '17bc4b457503'
branch_labels = None
depends_on = None


from orchestrator.migrations.helpers import create_workflow, delete_workflow

new_workflows = [
    {
        "name": "modify_circuit",
        "target": "MODIFY",
        "description": "Modify Circuit",
        "product_type": "Circuit"
    },
    {
        "name": "terminate_circuit",
        "target": "TERMINATE",
        "description": "Terminate Circuit",
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
