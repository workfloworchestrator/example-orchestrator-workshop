# pylint: disable=missing-timeout
import re
import structlog


from tests.integration_tests.helpers import (
    # create_user,
    # create_user_group,
    create_node,
    create_circuit,
    get_domain_model,
)


logger = structlog.get_logger(__name__)

# def test_create_user_group_empty(products):
#     group_name = "Group One"

#     group_id = create_user_group(products, group_name)

#     group = get_domain_model(group_id)

#     assert group["description"] == f"User Group {group_name}"
#     assert group["product"]["name"] == "User Group"
#     assert group["user_group"]["group_name"] == group_name


# def test_create_user_group_with_users(products):
#     group_name = "Group Two"

#     group_id = create_user_group(products, group_name)

#     user_ext_id = create_user(products, group_id, "User external", "my_external_user", 30)
#     user_int_id = create_user(products, group_id, "User internal", "my_internal_user", 40)

#     user_ext = get_domain_model(user_ext_id)
#     user_int = get_domain_model(user_int_id)

#     assert user_ext["description"] == "User my_external_user from group Group Two (external)"
#     assert user_int["description"] == "User my_internal_user from group Group Two (internal)"

#     assert user_ext["user"]["group"]["group_name"] == group_name
#     assert user_int["user"]["group"]["group_name"] == group_name


def test_create_nodes(products):
    logger.info("Running test_create_node ")
    node_names = ["loc1-core", "loc2-core", "loc3-core", "loc4-core", "loc5-core"]
    for node in node_names:
        logger.info(f"Attempting to enroll node {node}")
        node_id = create_node(products, node)
        logger.info(f"Node {node} sucessfully enrolled with subscription ID: {node_id}")
        node_model = get_domain_model(node_id)

        assert node_model["description"] == f"Node {node} Subscription"
        assert node_model["node"]["node_name"] == node

        assert node_model["node"]["ipv4_loopback"] == f"10.0.0.{node[3]}"
        assert node_model["node"]["ipv6_loopback"] == f"2001:db8::{node[3]}"

        logger.info(f"All assertions pass for Node Subscription for {node}")


def test_create_circuit(products):
    logger.info("Running test_create_circuit ")
    circuit_names = [
        "Circuit ID 7: loc1-core:1/1/c2/1 <--> loc2-core:1/1/c1/1",
        "Circuit ID 8: loc1-core:1/1/c3/1 <--> loc3-core:1/1/c1/1",
        "Circuit ID 9: loc1-core:1/1/c4/1 <--> loc4-core:1/1/c1/1",
        "Circuit ID 10: loc1-core:1/1/c5/1 <--> loc5-core:1/1/c1/1",
        "Circuit ID 11: loc2-core:1/1/c3/1 <--> loc3-core:1/1/c2/1",
        "Circuit ID 12: loc2-core:1/1/c4/1 <--> loc4-core:1/1/c2/1",
        "Circuit ID 13: loc2-core:1/1/c5/1 <--> loc5-core:1/1/c2/1",
        "Circuit ID 14: loc3-core:1/1/c4/1 <--> loc4-core:1/1/c3/1",
        "Circuit ID 15: loc3-core:1/1/c5/1 <--> loc5-core:1/1/c3/1",
        "Circuit ID 16: loc4-core:1/1/c5/1 <--> loc5-core:1/1/c4/1",
    ]
    # node_names = ["loc5-core"]
    for circuit in circuit_names:
        logger.info(f'Attempting to provision Circuit "{circuit}"')
        circuit_sub_id = create_circuit(products, circuit)
        logger.info(
            f'Circuit subscription "{circuit}" sucessfully run with subscription ID: {circuit_sub_id}'
        )
        circuit_model = get_domain_model(circuit_sub_id)

        parsed_circuit = re.search(
            r"Circuit\sID\s(\d+):\s(\S+):(\S+)\s\S+\s(\S+):(\S+)", circuit
        )

        assert circuit_model["description"] == f"Subscription for {circuit}"
        assert circuit_model["ckt"]["circuit_id"] == int(parsed_circuit[1])

        assert circuit_model["ckt"]["under_maintenance"] == True

        # Test A-Side Data
        assert (
            circuit_model["ckt"]["members"][0]["port"]["node"]["node_name"]
            == parsed_circuit[2]
        )
        assert (
            circuit_model["ckt"]["members"][0]["port"]["port_name"] == parsed_circuit[3]
        )
        assert (
            circuit_model["ckt"]["members"][0]["port"]["port_description"]
            == f"Circuit Connection to {parsed_circuit[4]} port {parsed_circuit[5]}"
        )

        # Test B-Side Data
        assert (
            circuit_model["ckt"]["members"][1]["port"]["node"]["node_name"]
            == parsed_circuit[4]
        )
        assert (
            circuit_model["ckt"]["members"][1]["port"]["port_name"] == parsed_circuit[5]
        )
        assert (
            circuit_model["ckt"]["members"][1]["port"]["port_description"]
            == f"Circuit Connection to {parsed_circuit[2]} port {parsed_circuit[3]}"
        )
