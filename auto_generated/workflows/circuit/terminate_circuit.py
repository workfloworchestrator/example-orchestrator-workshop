# Copyright 2019-2022 SURF.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from orchestrator.types import State, UUIDstr
from orchestrator.workflow import StepList, begin, step

from surf.products.product_types.circuit import Circuit

from surf.workflows.workflow import terminate_initial_input_form_generator, terminate_workflow


@step("Load initial state")
def load_initial_state(subscription: Circuit) -> State:
    # TODO: optionally add additional values.
    # Copy values to the root of the state for easy access

    return {
        "subscription": subscription,
    }



@terminate_workflow("Terminate Circuit", initial_input_form=terminate_initial_input_form_generator)
def terminate_circuit() -> StepList:
    return (
        begin
        >> load_initial_state
        # TODO: fill in additional steps if needed
    )