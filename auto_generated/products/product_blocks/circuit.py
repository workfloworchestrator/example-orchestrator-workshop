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



from typing import TypeVar


from orchestrator.domain.base import ProductBlockModel, serializable_property
from orchestrator.types import SubscriptionLifecycle


T = TypeVar("T", covariant=True)


class ListOfMembers(SubscriptionInstanceList[T]):
    min_items = 2
    max_items = 2
    



class CircuitBlockInactive(ProductBlockModel, product_block_name="Circuit"):
    members: ListOfMembers[Layer3InterfaceBlockInactive]
    circuit_id: int | None = None 
    under_maintenance: bool | None = None 
    

class CircuitBlockProvisioning(CircuitBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    members: ListOfMembers[Layer3InterfaceBlock]
    circuit_id: int 
    under_maintenance: bool 
    
    @serializable_property
    def title(self) -> str:
        # TODO: format correct title string
        return f"{self.name}"


class CircuitBlock(CircuitBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    members: ListOfMembers[Layer3InterfaceBlock]
    circuit_id: int 
    under_maintenance: bool 
    