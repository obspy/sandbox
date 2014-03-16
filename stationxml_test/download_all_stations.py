#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Downloads the response level StationXML file for all stations in the file
'all_stations.xml' which contains a station level StationXML file.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2014
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""
import colorama
from obspy.station import read_inventory
from obspy.fdsn import Client
import os

output_dir = "StationXML"

c = Client()

inv = read_inventory("./all_stations.xml")


def print_error(msg):
    print colorama.Fore.RED + msg + colorama.Fore.RESET


def print_ok(msg):
    print colorama.Fore.GREEN + msg + colorama.Fore.RESET


for network in inv.networks:
    for station in network.stations:
        output_filename = os.path.join(output_dir, "%s.%s.xml" %
                                       (network.code, station.code))
        if os.path.exists(output_filename):
            continue

        try:
            out = c.get_stations(network=network.code, station=station.code,
                                 level="response")
        except:
            print_error("Failed to download %s.%s." % (network.code,
                                                       station.code))
            continue
        with open(output_filename, "w") as fh:
            fh.write(out)
        print_ok("Downloaded %s.%s." % (network.code, station.code))
