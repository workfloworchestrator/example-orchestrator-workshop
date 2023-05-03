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


from orchestrator.domain.base import SubscriptionModel
from orchestrator.types import SubscriptionLifecycle

from surf.products.product_blocks.circuit import (
    CircuitBlock,
    CircuitBlockInactive,
    CircuitBlockProvisioning,
)

from surf.products.product_types.fixed_input_types import Speed
class CircuitInactive(SubscriptionModel, is_base=True):
    speed: Speed
    ckt: CircuitBlockInactive
    

class CircuitProvisioning(CircuitInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    speed: Speed
    ckt: CircuitBlockProvisioning
    

class Circuit(CircuitProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    speed: Speed
    ckt: CircuitBlock
    
