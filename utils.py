from netbox import NetBox  # type: ignore

netbox = NetBox(
    host="netlab-rover7.es.net",
    port=8000,
    use_ssl=False,
    auth_token="e744057d755255a31818bf74df2350c26eeabe54",
)
