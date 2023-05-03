import pytest
from orchestrator.forms import FormValidationError

from orchestrator.types import SubscriptionLifecycle
from test.unit_tests.mock import CrmMocks
from test.unit_tests.workflows import assert_complete, extract_state, run_workflow

from surf.products.product_types.circuit import Circuit


@pytest.mark.workflow
def test_happy_flow(responses, circuit_subscription):
    # given

    customer_id = "3f4fc287-0911-e511-80d0-005056956c1a"
    crm = CrmMocks(responses)
    crm.get_organisation_by_uuid(customer_id)

    # TODO insert additional mocks, if needed (ImsMocks)

    # when

    init_state = {}

    result, process, step_log = run_workflow(
        "modify_circuit", [{"subscription_id": circuit_subscription}, init_state, {}]
    )

    # then

    assert_complete(result)
    state = extract_state(result)

    circuit = Circuit.from_subscription(state["subscription_id"])
    assert circuit.status == SubscriptionLifecycle.ACTIVE

