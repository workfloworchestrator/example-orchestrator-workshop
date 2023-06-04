from uuid import uuid4

from orchestrator.db import ProductTable, db
from orchestrator.types import SubscriptionLifecycle

from products.product_types.node import Node, NodeInactive


def test_node_new():
    product = ProductTable.query.filter(ProductTable.name == "node").one()

    diff = Node.diff_product_in_database(product.product_id)
    assert diff == {}

    node = NodeInactive.from_product_id(
        product_id=product.product_id, customer_id=uuid4(), status=SubscriptionLifecycle.INITIAL
    )

    assert node.subscription_id is not None
    assert node.insync is False

    # TODO: Add more product specific asserts

    assert node.description == f"Initial subscription of {product.description}"
    node.save()

    node2 = NodeInactive.from_subscription(node.subscription_id)
    assert node == node2


def test_node_load_and_save_db(node_subscription):
    node = Node.from_subscription(node_subscription)

    assert node.insync is True

    # TODO: Add more product specific asserts

    node.description = "Changed description"

    # TODO: add a product specific change

    node.save()

    # Explicit commit here as we are not running in the context of a step
    db.session.commit()

    node = Node.from_subscription(node_subscription)

    # TODO: Add more product specific asserts

    assert node.description == "Changed description"