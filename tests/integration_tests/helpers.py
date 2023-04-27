# pylint: disable=missing-timeout, missing-function-docstring
import time

import requests

import structlog


API_URL = "http://127.0.0.1:8080/api"


logger = structlog.get_logger(__name__)


def response_to_json(response):
    assert response.ok, f"Response not ok: {response.text}"
    return response.json()


def resume_workflow(
    process_id: str, resume_field: str = "confirm_config_put_on_routers"
):
    logger.info(f"Attempting to resume workflow with PID: {process_id}")
    resume_response = requests.put(
        f"{API_URL}/processes/{process_id}/resume",
        json=[{resume_field: "ACCEPTED"}],
    )
    assert resume_response.ok, f"Response not ok: {resume_response.status_code}"
    logger.info(f"Successfully resumed workflow with PID: {process_id}")


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


def wait_process_complete_user_input(process_id: str) -> str:
    """Wait for the given process to complete and then return the subscription id."""
    process_result = {"status": None}

    logger.info(f"Waiting for PID {process_id} to complete")

    i = 0
    while not process_result["status"] == "completed":
        i += 1
        status_response = requests.get(f"{API_URL}/processes/{process_id}")
        process_result = response_to_json(status_response)
        logger.info(
            f"PID {process_id} is currently {process_result['status']} after {i} iterations"
        )
        if process_result["status"] == "suspended":
            resume_workflow(process_id=process_id)
        if i >= 10:
            logger.error(f"Proccess not completed ater {i} waiting cycles.")
            break
        time.sleep(0.5)

    assert process_result["status"] == "completed"

    logger.info(
        f"PID {process_id} status was successfully completed after {i} iterations"
    )

    return process_result["subscriptions"][0]["subscription_id"]


def get_domain_model(subscription_id: str) -> dict:
    domain_model_response = requests.get(
        f"{API_URL}/subscriptions/domain-model/{subscription_id}"
    )
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


def create_node(products, node_name):
    product_id = products["Node"]

    create_response = requests.post(
        f"{API_URL}/processes/create_node",
        json=[{"product": product_id}, {"select_node_choice": node_name}],
    )
    product = response_to_json(create_response)
    subscription_id = wait_process_complete_user_input(product["id"])
    return subscription_id


def create_circuit(products, circuit_name):
    product_id = products["Circuit"]

    create_response = requests.post(
        f"{API_URL}/processes/create_circuit",
        json=[{"product": product_id}, {"select_circuit_choice": circuit_name}],
    )
    product = response_to_json(create_response)
    subscription_id = wait_process_complete_user_input(product["id"])
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
