import pytest

from orchestrator.db import ProductTable
from orchestrator.forms import FormValidationError

from test.unit_tests.mock import CrmMocks
from test.unit_tests.workflows import assert_complete, extract_state, run_workflow

from surf.products.product_types.ws_node import node


@pytest.mark.workflow
def test_happy_flow(responses):
    # given

    customer_id = "3f4fc287-0911-e511-80d0-005056956c1a"
    crm = CrmMocks(responses)
    crm.get_organisation_by_uuid(customer_id)

    # TODO insert additional mocks, if needed (ImsMocks)

    product = ProductTable.query.filter(ProductTable.name == "Node").one()

    # when

    init_state = {
        "organisation": customer_id,
        # TODO add initial state
    }

    result, process, step_log = run_workflow("create_ws_node", [{"product": product.product_id}, init_state])

    # then

    assert_complete(result)
    state = extract_state(result)

    subscription = node.from_subscription(state["subscription_id"])
    assert subscription.status == "active"
    assert subscription.description == "TODO add correct description"

