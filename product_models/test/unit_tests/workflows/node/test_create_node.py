import pytest

from orchestrator.db import ProductTable
from orchestrator.forms import FormValidationError

from test.unit_tests.workflows import assert_complete, extract_state, run_workflow

from products.product_types.node import Node


@pytest.mark.workflow
def test_happy_flow(responses):
    # given

    # TODO insert additional mocks, if needed (ImsMocks)

    product = ProductTable.query.filter(ProductTable.name == "node").one()

    # when

    init_state = {
        "organisation": customer_id,
        # TODO add initial state
    }

    result, process, step_log = run_workflow("create_node", [{"product": product.product_id}, init_state])

    # then

    assert_complete(result)
    state = extract_state(result)

    subscription = Node.from_subscription(state["subscription_id"])
    assert subscription.status == "active"
    assert subscription.description == "TODO add correct description"

