from tests.integration_tests.helpers import (
    create_user,
    create_user_group,
    get_domain_model,
)


def test_create_user_group_empty(products):
    group_name = "Group One"

    group_id = create_user_group(products, group_name)

    group = get_domain_model(group_id)

    assert group["description"] == f"User Group {group_name}"
    assert group["product"]["name"] == "User Group"
    assert group["user_group"]["group_name"] == group_name


def test_create_user_group_with_users(products):
    group_name = "Group Two"

    group_id = create_user_group(products, group_name)

    user_ext_id = create_user(products, group_id, "User external", "my_external_user", 30)
    user_int_id = create_user(products, group_id, "User internal", "my_internal_user", 40)

    user_ext = get_domain_model(user_ext_id)
    user_int = get_domain_model(user_int_id)

    assert user_ext["description"] == "User my_external_user from group Group Two (external)"
    assert user_int["description"] == "User my_internal_user from group Group Two (internal)"

    assert user_ext["user"]["group"]["group_name"] == group_name
    assert user_int["user"]["group"]["group_name"] == group_name
