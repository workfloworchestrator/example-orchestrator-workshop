from netbox import NetBox  # type: ignore

netbox = NetBox(
    host="netbox",
    port=8080,
    use_ssl=False,
    auth_token="e744057d755255a31818bf74df2350c26eeabe54",
)
