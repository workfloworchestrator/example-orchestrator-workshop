from uuid import UUID

from orchestrator import begin, step
from orchestrator.forms import FormPage
from orchestrator.types import State, FormGenerator
from orchestrator.workflow import StepList
from structlog import get_logger

from products import Circuit
from workflows.shared import modify_workflow

logger = get_logger(__name__)


def modify_initial_input_form_generator(subscription_id: UUID) -> FormGenerator:
    subscription = Circuit.from_subscription(subscription_id)

    class ChangeSpeed(FormPage):
        # add more options that can be changed.
        speed: int = subscription.speed

    user_input = yield ChangeSpeed

    logger.debug("User input is", user_input=user_input)

    return user_input.dict()


@step("Modify")
def modify(subscription: Circuit) -> State:
    logger.debug("This is the subscription", subscription=subscription, type=type(subscription))
    # DO SOMETHING
    return {}


@modify_workflow("Modify the circuit", initial_input_form=modify_initial_input_form_generator)
def modify_circuit() -> StepList:
    return begin >> modify
