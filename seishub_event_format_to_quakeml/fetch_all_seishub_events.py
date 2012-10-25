#!/usr/bin/env python
from obspy.seishub import Client
client = Client('http://10.153.82.3:8080', timeout=120, retries=10)
llist = client.event.getList(limit=2500)
offset = 0
while len(llist) % 2500 == 0:
    offset += 1
    llist += client.event.getList(limit=2500, offset=offset*2400)
llist = set(llist)
llist2 = [d['resource_name'] for d in llist]
llist2 = set(llist2)
llist2 = list(llist2)
llist2[1351] = str(llist2[1351])
open("all_resource_names", "w").write("\n".join(list(llist2)))
