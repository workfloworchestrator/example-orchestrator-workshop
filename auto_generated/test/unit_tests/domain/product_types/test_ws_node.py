from uuid import uuid4

from orchestrator.db import ProductTable, db
from orchestrator.types import SubscriptionLifecycle

from surf.products.product_types.ws_node import node, nodeInactive


def test_ws_node_new():
    product = ProductTable.query.filter(ProductTable.name == "Node").one()

    diff = node.diff_product_in_database(product.product_id)
    assert diff == {}

    ws_node = nodeInactive.from_product_id(
        product_id=product.product_id, customer_id=uuid4(), status=SubscriptionLifecycle.INITIAL
    )

    assert ws_node.subscription_id is not None
    assert ws_node.insync is False

    # TODO: Add more product specific asserts

    assert ws_node.description == f"Initial subscription of {product.description}"
    ws_node.save()

    ws_node2 = nodeInactive.from_subscription(ws_node.subscription_id)
    assert ws_node == ws_node2


def test_ws_node_load_and_save_db(ws_node_subscription):
    ws_node = node.from_subscription(ws_node_subscription)

    assert ws_node.insync is True

    # TODO: Add more product specific asserts

    ws_node.description = "Changed description"
    # TODO: add a product specific change
    ws_node.save()

    # Explicit commit here as we are not running in the context of a step
    db.session.commit()

    ws_node = node.from_subscription(ws_node_subscription)
    # TODO: Add more product specific asserts
    assert ws_node.description == "Changed description"