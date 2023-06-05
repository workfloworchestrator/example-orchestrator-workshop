

from typing import Optional


from typing import TypeVar
from orchestrator.domain.base import SubscriptionInstanceList

from pydantic import ConstrainedInt


from products.product_blocks import Layer3InterfaceBlock, Layer3InterfaceBlockInactive, Layer3InterfaceBlockProvisioning

from orchestrator.domain.base import ProductBlockModel, serializable_property
from orchestrator.types import SubscriptionLifecycle


T = TypeVar("T", covariant=True)


class ListOfMembers(SubscriptionInstanceList[T]):
    min_items = 2
    max_items = 2
    



class CircuitId(ConstrainedInt):
     ge = 1 
     le = 32_767 



class CircuitBlockInactive(ProductBlockModel, product_block_name="Circuit"):
    members: ListOfMembers[Layer3InterfaceBlockInactive]
    circuit_id: Optional[CircuitId] = None 
    under_maintenance: Optional[bool] = None 
    


class CircuitBlockProvisioning(CircuitBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    members: ListOfMembers[Layer3InterfaceBlock]
    circuit_id: CircuitId 
    under_maintenance: bool 
    
    @serializable_property
    def title(self) -> str:
        # TODO: format correct title string
        return f"{self.name}"


class CircuitBlock(CircuitBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    members: ListOfMembers[Layer3InterfaceBlock]
    circuit_id: CircuitId 
    under_maintenance: bool 
    