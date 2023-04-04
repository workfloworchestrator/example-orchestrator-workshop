from orchestrator.workflow import StepList, begin
from orchestrator.workflows.utils import validate_workflow
from workflows.shared import load_node_subscription_info, is_active


@validate_workflow("Validate Node")
def validate_node() -> StepList:
    return (
        begin
        >> load_node_subscription_info
        >> is_active()
    )
