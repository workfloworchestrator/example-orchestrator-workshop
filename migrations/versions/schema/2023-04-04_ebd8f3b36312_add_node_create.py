"""add node and circuit create and validate workflows.

Revision ID: ebd8f3b36312
Revises: 31bd7676d11e
Create Date: 2023-04-04 14:15:01.848156

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'ebd8f3b36312'
down_revision = '31bd7676d11e'
branch_labels = None
depends_on = None


from orchestrator.migrations.helpers import create_workflow, delete_workflow

new_workflows = [
    {
        "name": "create_node",
        "target": "CREATE",
        "description": "Create Node",
        "product_type": "Node"
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
