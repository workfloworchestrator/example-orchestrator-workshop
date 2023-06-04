

from typing import Optional

from ipaddress import IPv4Address
from ipaddress import IPv6Address


from orchestrator.domain.base import ProductBlockModel, serializable_property
from orchestrator.types import SubscriptionLifecycle




class NodeBlockInactive(ProductBlockModel, product_block_name="Node"):
    node_id: Optional[int] = None 
    node_name: Optional[str] = None 
    ipv4_loopback: Optional[IPv4Address] = None 
    ipv6_loopback: Optional[IPv6Address] = None 
    


class NodeBlockProvisioning(NodeBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    node_id: int 
    node_name: str 
    ipv4_loopback: IPv4Address 
    ipv6_loopback: IPv6Address 
    
    @serializable_property
    def title(self) -> str:
        # TODO: format correct title string
        return f"{self.name}"


class NodeBlock(NodeBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    node_id: int 
    node_name: str 
    ipv4_loopback: IPv4Address 
    ipv6_loopback: IPv6Address 
    