

from typing import Optional

from ipaddress import IPv6Interface


from products.product_blocks import PortBlock, PortBlockInactive, PortBlockProvisioning

from orchestrator.domain.base import ProductBlockModel, serializable_property
from orchestrator.types import SubscriptionLifecycle




class Layer3InterfaceBlockInactive(ProductBlockModel, product_block_name="Layer3 Interface"):
    port: Optional[PortBlockInactive] = None 
    v6_ip_address: Optional[IPv6Interface] = None 
    


class Layer3InterfaceBlockProvisioning(Layer3InterfaceBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    port: Optional[PortBlockProvisioning] = None 
    v6_ip_address: IPv6Interface 
    
    @serializable_property
    def title(self) -> str:
        # TODO: format correct title string
        return f"{self.name}"


class Layer3InterfaceBlock(Layer3InterfaceBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    port: Optional[PortBlock] = None 
    v6_ip_address: IPv6Interface 
    