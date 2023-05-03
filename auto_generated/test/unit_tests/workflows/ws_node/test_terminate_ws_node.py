import pytest


from orchestrator.types import SubscriptionLifecycle
from test.unit_tests.workflows import assert_complete, extract_state, run_workflow

from surf.products.product_types.ws_node import node


@pytest.mark.workflow
def test_happy_flow(responses, ws_node_subscription):
    # when

    # TODO: insert mocks here if needed (ImsMocks, NsoMocks)

    result, _, _ = run_workflow("terminate_ws_node", [{"subscription_id": ws_node_subscription}, {}])

    # then

    assert_complete(result)
    state = extract_state(result)
    assert "subscription" in state

    # Check subscription in DB

    ws_node = node.from_subscription(ws_node_subscription)
    assert ws_node.end_date is not None
    assert ws_node.status == SubscriptionLifecycle.TERMINATED

