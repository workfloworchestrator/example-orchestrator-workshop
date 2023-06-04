import pytest
from orchestrator.forms import FormValidationError

from orchestrator.types import SubscriptionLifecycle
from test.unit_tests.workflows import assert_complete, extract_state, run_workflow

from products.product_types.node import Node


@pytest.mark.workflow
def test_happy_flow(responses, node_subscription):
    # given

    customer_id = "3f4fc287-0911-e511-80d0-005056956c1a"
    crm = CrmMocks(responses)
    crm.get_organisation_by_uuid(customer_id)

    # TODO insert additional mocks, if needed (ImsMocks)

    # when

    init_state = {}

    result, process, step_log = run_workflow(
        "modify_node", [{"subscription_id": node_subscription}, init_state, {}]
    )

    # then

    assert_complete(result)
    state = extract_state(result)

    node = Node.from_subscription(state["subscription_id"])
    assert node.status == SubscriptionLifecycle.ACTIVE

