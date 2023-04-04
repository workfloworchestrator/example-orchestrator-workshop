from tests.integration_tests.helpers import (
    create_user_group,
    get_domain_model,
    modify_user_group,
)


def test_modify_user_group(products):
    group_name = "Group One"

    group_id = create_user_group(products, group_name)

    group = get_domain_model(group_id)
    assert group["user_group"]["group_name"] == group_name

    _ = modify_user_group(f"{group_name} Modified", group_id)

    group_modified = get_domain_model(group_id)
    assert group_modified["user_group"]["group_name"] == f"{group_name} Modified"
