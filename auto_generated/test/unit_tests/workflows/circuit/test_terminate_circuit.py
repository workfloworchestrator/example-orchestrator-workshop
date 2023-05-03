import pytest


from orchestrator.types import SubscriptionLifecycle
from test.unit_tests.workflows import assert_complete, extract_state, run_workflow

from surf.products.product_types.circuit import Circuit


@pytest.mark.workflow
def test_happy_flow(responses, circuit_subscription):
    # when

    # TODO: insert mocks here if needed (ImsMocks, NsoMocks)

    result, _, _ = run_workflow("terminate_circuit", [{"subscription_id": circuit_subscription}, {}])

    # then

    assert_complete(result)
    state = extract_state(result)
    assert "subscription" in state

    # Check subscription in DB

    circuit = Circuit.from_subscription(circuit_subscription)
    assert circuit.end_date is not None
    assert circuit.status == SubscriptionLifecycle.TERMINATED

