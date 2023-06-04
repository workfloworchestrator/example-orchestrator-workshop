import pytest


from orchestrator.forms import FormValidationError

from orchestrator.types import SubscriptionLifecycle
from test.unit_tests.workflows import assert_complete, extract_state, run_workflow

from products.product_types.circuit import Circuit


@pytest.mark.workflow
def test_happy_flow(responses, circuit_subscription):
    # when

    # TODO: insert mocks here if needed

    result, _, _ = run_workflow("terminate_circuit", [{"subscription_id": circuit_subscription}, {}])

    # then

    assert_complete(result)
    state = extract_state(result)
    assert "subscription" in state

    # Check subscription in DB

    circuit = Circuit.from_subscription(circuit_subscription)
    assert circuit.end_date is not None
    assert circuit.status == SubscriptionLifecycle.TERMINATED


@pytest.mark.workflow
def test_can_only_terminate_when_under_maintenance(responses, circuit_subscription):
    # given

    # TODO: set test conditions or fixture so that "Delete the circuit only when placed under maintenance" triggers

    # when

    with pytest.raises(FormValidationError) as error:
        result, _, _ = run_workflow("terminate_circuit", [{"subscription_id": circuit_subscription}, {}])

    # then

    assert error.value.errors[0]["msg"] == "Delete the circuit only when placed under maintenance"

