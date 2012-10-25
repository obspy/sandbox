#!/usr/bin/env python
from obspy.seishub import Client

client = Client('http://10.153.82.3:8080', timeout=120, retries=10)
events = client.event.getList(limit=2500)
offset = 0
# shift offset until less than 2500 new events get added
while len(events) % 2500 == 0:
    offset += 1
    events += client.event.getList(limit=2500, offset=offset*2400)
resource_names = [d['resource_name'] for d in events]
# make a unique list
resource_names = list(set(resource_names))
# one resource name got converted to an int on server side..
resource_names = map(str, resource_names)
with open("all_resource_names", "w") as fh:
    fh.write("\n".join(list(resource_names)))
