from uuid import uuid4

from orchestrator.db import ProductTable, db
from orchestrator.types import SubscriptionLifecycle

from surf.products.product_types.circuit import Circuit, CircuitInactive


def test_circuit_new():
    product = ProductTable.query.filter(ProductTable.name == "Circuit").one()

    diff = Circuit.diff_product_in_database(product.product_id)
    assert diff == {}

    circuit = CircuitInactive.from_product_id(
        product_id=product.product_id, customer_id=uuid4(), status=SubscriptionLifecycle.INITIAL
    )

    assert circuit.subscription_id is not None
    assert circuit.insync is False

    # TODO: Add more product specific asserts

    assert circuit.description == f"Initial subscription of {product.description}"
    circuit.save()

    circuit2 = CircuitInactive.from_subscription(circuit.subscription_id)
    assert circuit == circuit2


def test_circuit_load_and_save_db(circuit_subscription):
    circuit = Circuit.from_subscription(circuit_subscription)

    assert circuit.insync is True

    # TODO: Add more product specific asserts

    circuit.description = "Changed description"
    # TODO: add a product specific change
    circuit.save()

    # Explicit commit here as we are not running in the context of a step
    db.session.commit()

    circuit = Circuit.from_subscription(circuit_subscription)
    # TODO: Add more product specific asserts
    assert circuit.description == "Changed description"