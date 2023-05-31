from typing import Optional

from orchestrator.domain.base import ProductBlockModel
from orchestrator.types import SubscriptionLifecycle


class UserGroupBlockInactive(
    ProductBlockModel,
    lifecycle=[SubscriptionLifecycle.INITIAL],
    product_block_name="UserGroupBlock",
):
    group_name: Optional[str] = None
    group_id: Optional[int] = None


class UserGroupBlockProvisioning(
    UserGroupBlockInactive, lifecycle=[SubscriptionLifecycle.PROVISIONING]
):
    group_name: str
    group_id: Optional[int] = None


class UserGroupBlock(
    UserGroupBlockProvisioning, lifecycle=[SubscriptionLifecycle.ACTIVE]
):
    group_name: str
    group_id: int
