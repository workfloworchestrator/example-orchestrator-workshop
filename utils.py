from netbox import NetBox # type: ignore

netbox = NetBox(host='127.0.0.1', port=32768, use_ssl=False, auth_token='token')