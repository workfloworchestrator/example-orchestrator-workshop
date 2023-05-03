import pytest
from orchestrator.forms import FormValidationError

from orchestrator.types import SubscriptionLifecycle
from test.unit_tests.mock import CrmMocks
from test.unit_tests.workflows import assert_complete, extract_state, run_workflow

from surf.products.product_types.ws_node import node


@pytest.mark.workflow
def test_happy_flow(responses, ws_node_subscription):
    # given

    customer_id = "3f4fc287-0911-e511-80d0-005056956c1a"
    crm = CrmMocks(responses)
    crm.get_organisation_by_uuid(customer_id)

    # TODO insert additional mocks, if needed (ImsMocks)

    # when

    init_state = {}

    result, process, step_log = run_workflow(
        "modify_ws_node", [{"subscription_id": ws_node_subscription}, init_state, {}]
    )

    # then

    assert_complete(result)
    state = extract_state(result)

    ws_node = node.from_subscription(state["subscription_id"])
    assert ws_node.status == SubscriptionLifecycle.ACTIVE

