import structlog
from orchestrator.forms import FormPage, ReadOnlyField
from orchestrator.forms.validators import Choice, OrganisationId
from orchestrator.targets import Target
from orchestrator.types import FormGenerator, SubscriptionLifecycle
from orchestrator.types import InputForm, InputStepFunc, SubscriptionLifecycle, UUIDstr
from orchestrator.workflow import StepList, Workflow, done, init, make_workflow
from orchestrator.workflows.utils import wrap_create_initial_input_form
from orchestrator.workflows.steps import resync, set_status, store_process_subscription

from orchestrator.workflow import StepList, begin
from orchestrator.workflows.steps import set_status, store_process_subscription
from pydantic import validator
from typing import Any, Callable, Dict, Optional



logger = structlog.get_logger(__name__)

CUSTOMER_UUID = "b727dd2c-55f3-4d19-8452-a32f15b00123"

def create_workflow(
    description: str,
    initial_input_form: Optional[InputStepFunc] = None,
    status: SubscriptionLifecycle = SubscriptionLifecycle.ACTIVE,
) -> Callable[[Callable[[], StepList]], Workflow]:
    """Transform an initial_input_form and a step list into a workflow with a target=Target.CREATE.

    Use this for create workflows only.

    Example::

        @create_workflow("create service port")
        def create_service_port() -> StepList:
            do_something
            >> do_something_else
    """
    create_initial_input_form_generator = wrap_create_initial_input_form(initial_input_form)

    def _create_workflow(f: Callable[[], StepList]) -> Workflow:
        steplist = init >> f() >> set_status(status) >> resync >> done
        return make_workflow(f, description, create_initial_input_form_generator, Target.CREATE, steplist)

    return _create_workflow