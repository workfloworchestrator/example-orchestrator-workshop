import pytest


from orchestrator.types import SubscriptionLifecycle
from test.unit_tests.workflows import assert_complete, extract_state, run_workflow

from products.product_types.node import Node


@pytest.mark.workflow
def test_happy_flow(responses, node_subscription):
    # when

    # TODO: insert mocks here if needed

    result, _, _ = run_workflow("terminate_node", [{"subscription_id": node_subscription}, {}])

    # then

    assert_complete(result)
    state = extract_state(result)
    assert "subscription" in state

    # Check subscription in DB

    node = Node.from_subscription(node_subscription)
    assert node.end_date is not None
    assert node.status == SubscriptionLifecycle.TERMINATED

