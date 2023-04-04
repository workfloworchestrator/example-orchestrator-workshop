import time

import requests

API_URL = "http://127.0.0.1:8080/api"


def response_to_json(response):
    assert response.ok, f"Response not ok: {response.text}"
    return response.json()


def wait_process_complete(process_id: str) -> str:
    """Wait for the given process to complete and then return the subscription id."""
    process_result = None

    for _ in range(10):
        status_response = requests.get(f"{API_URL}/processes/{process_id}")
        process_result = response_to_json(status_response)
        if process_result["status"] == "completed":
            break
        time.sleep(0.5)

    assert process_result["status"] == "completed"

    return process_result["subscriptions"][0]["subscription_id"]


def get_domain_model(subscription_id: str) -> dict:
    domain_model_response = requests.get(f"{API_URL}/subscriptions/domain-model/{subscription_id}")
    return response_to_json(domain_model_response)


def create_user(products, group_id, user_type, user_name, user_age):
    user_product_id = products[user_type]
    create_user_response = requests.post(
        f"{API_URL}/processes/create_user",
        json=[
            {"product": user_product_id},
            {"user_group_ids": [group_id], "username": user_name, "age": user_age},
        ],
    )
    product = response_to_json(create_user_response)
    subscription_id = wait_process_complete(product["id"])
    return subscription_id


def create_user_group(products, group_name):
    product_id = products["User Group"]

    create_response = requests.post(
        f"{API_URL}/processes/create_user_group",
        json=[{"product": product_id}, {"group_name": group_name}],
    )
    product = response_to_json(create_response)
    subscription_id = wait_process_complete(product["id"])
    return subscription_id


def modify_user_group(new_group_name, subscription_id):
    modify_response = requests.post(
        f"{API_URL}/processes/modify_user_group",
        json=[{"subscription_id": subscription_id}, {"group_name": new_group_name}],
    )
    product = response_to_json(modify_response)
    subscription_id = wait_process_complete(product["id"])
    return subscription_id


def terminate_user_group(subscription_id):
    terminate_response = requests.post(
        f"{API_URL}/processes/terminate_user_group",
        json=[{"subscription_id": subscription_id}, {}],
    )
    product = response_to_json(terminate_response)
    subscription_id = wait_process_complete(product["id"])
    return subscription_id
