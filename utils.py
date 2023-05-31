import pynetbox # type: ignore

netbox = pynetbox.api(
    'http://netbox:8080',
    token='e744057d755255a31818bf74df2350c26eeabe54'
)
