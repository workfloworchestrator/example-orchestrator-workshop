from typing import Optional

from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SubscriptionLifecycle

from products.product_blocks.user_group import UserGroupBlock, UserGroupBlockInactive, UserGroupBlockProvisioning


class UserBlockInactive(ProductBlockModel, lifecycle=[SubscriptionLifecycle.INITIAL], product_block_name="UserBlock"):
    group: UserGroupBlockInactive
    username: Optional[str] = None
    age: Optional[int] = None
    user_id: Optional[int] = None


class UserBlockProvisioning(UserBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]):
    group: UserGroupBlockProvisioning
    username: str
    age: Optional[int] = None
    user_id: Optional[int] = None


class UserBlock(UserBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]):
    group: UserGroupBlock
    username: str
    age: Optional[int] = None
    user_id: int
