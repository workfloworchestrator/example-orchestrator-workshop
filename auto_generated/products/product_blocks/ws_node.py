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


from ipaddress import IPv4Address
from ipaddress import IPv6Address


from orchestrator.domain.base import ProductBlockModel, serializable_property
from orchestrator.types import SubscriptionLifecycle



class NodeBlockInactive(ProductBlockModel, product_block_name="Node"):
    node_id: int | None = None 
    node_name: str | None = None 
    ipv4_loopback: IPv4Address | None = None 
    ipv6_loopback: IPv6Address | None = None 
    

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
    