

from typing import Optional

from products.product_blocks.node import NodeBlock

from pydantic import ConstrainedInt


from orchestrator.domain.base import ProductBlockModel, serializable_property
from orchestrator.types import SubscriptionLifecycle



class PortId(ConstrainedInt):
     ge = 1 
     le = 32_767 



class PortBlockInactive(ProductBlockModel, product_block_name="Port"):
    port_id: Optional[PortId] = None 
    port_description: Optional[str] = None 
    port_name: Optional[str] = None 
    node: Optional[NodeBlock] = None 
    


class PortBlockProvisioning(PortBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    port_id: PortId 
    port_description: str 
    port_name: str 
    node: NodeBlock 
    
    @serializable_property
    def title(self) -> str:
        # TODO: format correct title string
        return f"{self.name}"


class PortBlock(PortBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    port_id: PortId 
    port_description: str 
    port_name: str 
    node: NodeBlock 
    