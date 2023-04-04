from collections.abc import Callable

import pytest
import requests

from tests.integration_tests.helpers import API_URL


@pytest.fixture
def products() -> dict[str, str]:
    """Return mapping from product name to product ids"""
    products_response = requests.get(f"{API_URL}/products")
    assert products_response.ok
    return {product["name"]: product["product_id"] for product in (products_response.json())}


@pytest.fixture
def get_subscriptions() -> Callable:
    def get() -> dict[str, dict]:
        subscriptions_response = requests.get(f"{API_URL}/subscriptions/all")
        assert subscriptions_response.ok
        return {sub["subscription_id"]: sub for sub in subscriptions_response.json()}

    return get


@pytest.fixture
def get_subscription_processes():
    def get(subscription_id: str) -> dict[str, dict]:
        processes_response = requests.get(
            f"{API_URL}/processes/process-subscriptions-by-subscription-id/{subscription_id}"
        )
        assert processes_response.ok
        return {process["pid"]: process for process in processes_response.json()}

    return get


@pytest.fixture(autouse=True)
def clean(get_subscriptions, get_subscription_processes):
    yield

    for sub_id, details in get_subscriptions().items():
        processes = get_subscription_processes(sub_id)
        for pid, _ in processes.items():
            assert requests.delete(f"{API_URL}/processes/{pid}").ok

        response = requests.delete(f"{API_URL}/subscriptions/{sub_id}")
        assert response.ok, f"Failed to delete subscription {sub_id} ({details['description']}): {response.text}"
