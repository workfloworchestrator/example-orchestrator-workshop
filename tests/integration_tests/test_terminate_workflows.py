from tests.integration_tests.helpers import (
    create_user_group,
    get_domain_model,
    terminate_user_group,
)


def test_terminate_user_group(products):
    group_name = "Group One"

    group_id = create_user_group(products, group_name)

    _ = terminate_user_group(group_id)

    group = get_domain_model(group_id)
    assert group["status"] == "terminated"
