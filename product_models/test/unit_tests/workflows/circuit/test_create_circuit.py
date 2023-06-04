import pytest

from orchestrator.db import ProductTable
from orchestrator.forms import FormValidationError

from test.unit_tests.workflows import assert_complete, extract_state, run_workflow

from products.product_types.circuit import Circuit


@pytest.mark.workflow
def test_happy_flow(responses):
    # given

    # TODO insert additional mocks, if needed (ImsMocks)

    product = ProductTable.query.filter(ProductTable.name == "Circuit").one()

    # when

    init_state = {
        "organisation": customer_id,
        # TODO add initial state
    }

    result, process, step_log = run_workflow("create_circuit", [{"product": product.product_id}, init_state])

    # then

    assert_complete(result)
    state = extract_state(result)

    subscription = Circuit.from_subscription(state["subscription_id"])
    assert subscription.status == "active"
    assert subscription.description == "TODO add correct description"


@pytest.mark.workflow
def test_circuit_id_must_be_unique(responses):
    # given

    customer_id = "3f4fc287-0911-e511-80d0-005056956c1a"

    product = ProductTable.query.filter(ProductTable.name == "Circuit"}}).one()

    # TODO set test conditions or fixture so that "circuit_id must be unique" triggers

    # when

    init_state = {
        "organisation": customer_id,
        # TODO add initial state
    }

    with pytest.raises(FormValidationError) as error:
        result, _, _ = run_workflow("create_circuit", [{"product": product.product_id}, init_state, {}])

    # then

    assert error.value.errors[0]["msg"] == "circuit_id must be unique"

