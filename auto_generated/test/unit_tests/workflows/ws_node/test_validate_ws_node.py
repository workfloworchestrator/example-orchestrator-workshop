import pytest

from test.unit_tests.workflows import assert_complete, extract_state, run_workflow


@pytest.mark.workflow
def test_happy_flow(responses, ws_node_subscription):
    # when

    result, process, step_log = run_workflow("validate_ws_node", {"subscription_id": ws_node_subscription})

    # then

    assert_complete(result)
    state = extract_state(result)
    assert state["check_core_db"] is True


