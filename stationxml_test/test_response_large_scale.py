#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test suite for the StationXML responses.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2013
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""
#import faulthandler
#faulthandler.enable()

import collections
import colorama
import fnmatch
import glob
import numpy as np
from obspy.core.util.misc import CatchOutput
from obspy.signal.invsim import evalresp
from obspy.station import read_inventory
from obspy.xseed import Parser
import os
import random
import warnings

from evresp_process import test_for_segfault

#channel_filter = []
#station_pattern = "IU.TUC"

channel_filter = []
station_pattern = ""

exclude_station_patterns = "EM.*"

#channel_filter = []
#station_pattern = "XN.CVCR"

debug = False

randomize = True
limit = 1000

if station_pattern:
    randomize = False
    limit = None


evil_channels = [
    "US.BMN..BLE",  # This channel has multiple similar blockettes per stage...
    "US.BMN..LLZ",  # This channel has multiple similar blockettes per stage...
]

# These are channels where evalresp does not apply the unit scaling.
faulty_evalresp = ["C.GO01.EP.LRO"]

stationxml = "StationXML/"
seed = "SEED/"


t_samp = 10.0
nfft = 16384
units = ["DISP", "ACC", "VEL"]


def print_error(msg):
    print colorama.Fore.RED + msg + colorama.Fore.RESET


def print_warning(msg):
    print colorama.Fore.YELLOW + msg + colorama.Fore.RESET


def print_info(msg):
    print colorama.Fore.BLUE + msg + colorama.Fore.RESET


def print_good(msg):
    print colorama.Fore.GREEN + msg + colorama.Fore.RESET


station_files = glob.glob(os.path.join(stationxml, "*.xml"))


counter = collections.Counter(
    correct_responses=0,
    faulty_responses=0,
    no_response_calculated_from_both=0,
    no_response_calculated_from_obspy=0,
    no_response_calculated_from_evalresp=0,
    evalresp_and_obsy_unit_error=0,
    only_obspy_unit_error=0,
    only_evalresp_unit_error=0,
    polynomial_response=0,
    evalresp_segfaults=0,
    duplicate_stage=0,
    random_error=0)


faulty_seed_files = []

# Loop over all StationXML files.
for _i in xrange(len(station_files)):
    if limit and _i >= limit:
        break

    if randomize:
        xml_file = random.choice(station_files)
    else:
        xml_file = station_files[_i]

    station_name = os.path.basename(xml_file).replace(".xml", "")

    if station_pattern and not fnmatch.fnmatch(station_name, station_pattern):
        continue

    if exclude_station_patterns and \
            fnmatch.fnmatch(station_name, exclude_station_patterns):
        continue

    print "File %i of %i (%s)..." % (_i + 1, len(station_files), xml_file)

    # Find the corresponding SEED file.
    seed_file = os.path.join(
        seed,
        os.path.splitext(
            os.path.basename(xml_file))[0] + os.path.extsep + "seed")
    if not os.path.exists(seed_file):
        msg = "Could not find SEED file '%s'. Will be skipped" % seed_file
        print_warning(msg)
        continue

    inv = read_inventory(xml_file, format="stationxml")
    net_id = inv[0].code
    stat_id = inv[0][0].code

    # Loop over every channel.
    for channel in inv[0][0]:

        # Nothing to be done if it has no response.
        if not channel.response:
            print_info("No response found...")
            continue

        if channel.end_date:
            date = channel.start_date + 0.5 * (channel.end_date -
                                               channel.start_date)
        else:
            date = channel.start_date + 86400

        loc_id = channel.location_code
        chan_id = channel.code

        chan = "%s.%s.%s.%s" % (net_id, stat_id, loc_id, chan_id)
        if chan in evil_channels:
            continue

        if channel_filter and chan not in channel_filter:
            continue

        # SEED Handling.
        if seed_file in faulty_seed_files:
            continue

        #from obspy import UTCDateTime
        #if channel.start_date != UTCDateTime(1999, 12, 28, 22, 24, 39):
            #continue

        print chan + ": ",

        unit_known_to_evalresp = True

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                p = Parser(seed_file)
            except:
                faulty_seed_files.append(seed_file)
                counter["random_error"] += 1
                print_warning("Failed to read SEED file!")
                continue

        try:
            all_resps = p.getRESP()
        except:
            counter["random_error"] += 1
            print_warning("getRESP() failed. Very likely a faulty SEED file")
            continue
        resp_string = "RESP.%s.%s.%s.%s" % (net_id, stat_id, loc_id, chan_id)
        all_resps = [_i for _i in all_resps if _i[0] == resp_string]

        if len(all_resps) != 1:
            msg = "Something fishy going on..."
            print_error(msg)
            break

        filename = all_resps[0][-1]

        for unit in units:
            filename.seek(0, 0)

            out = None
            seedresp_error = None

            # Get a set of all blockettes.
            blkts = set([int(i[1:4]) for i in filename.readlines()
                         if len(i) >= 4 and i[1:4].isdigit()])
            if blkts == set([50, 52, 58]):
                seedresp_error = "Not enough blockettes available"
                if debug:
                    print seedresp_error
            else:
                filename.seek(0, 0)

            if 62 in blkts:
                print_info("Polynomial response found. "
                           "Evalresp cannot deal with it")
                counter["polynomial_response"] += 1
                continue

            # Calculate the response by converting the SEED to RESP files and
            # passing those to evalresp.
            if not seedresp_error:
                output = test_for_segfault(t_samp, filename, date, stat_id,
                                           chan_id, net_id, loc_id, unit)
                if output == "segfault":
                    print_info("Raw evalresp segfaults. XML response not "
                               "attempted.")
                    counter["evalresp_segfaults"] += 1
                    continue
                elif not output:
                    filename.seek(0, 0)

                    if debug:
                        print "SEED"
                        try:
                            seed_response, seed_freq = evalresp(
                                t_samp, nfft, filename, date=date,
                                station=stat_id, channel=chan_id,
                                network=net_id, locid=loc_id, units=unit,
                                freq=True)
                        except ValueError as e:
                            seedresp_error = e
                    else:
                        with CatchOutput() as out:
                            try:
                                seed_response, seed_freq = evalresp(
                                    t_samp, nfft, filename, date=date,
                                    station=stat_id, channel=chan_id,
                                    network=net_id, locid=loc_id, units=unit,
                                    freq=True)
                            except ValueError as e:
                                seedresp_error = e
                elif output == "uniterror":
                    unit_known_to_evalresp = False
                else:
                    seedresp_error = output

            # Calculate the response by directly passing values from ObsPy to
            # evalresp.
            xml_resp_error = None
            duplicate_stage = None
            if not seedresp_error or seedresp_error == "uniterror":
                #print "CALCULATING RESPONE FROM XML!!!"
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    try:
                        with CatchOutput() as other_out:
                            xml_response, xml_freq = \
                                channel.response.get_evalresp_response(
                                    t_samp, nfft, output=unit)
                    except ValueError as e:
                        xml_resp_error = e

                    if "Each stage can only appear once" \
                            in str(xml_resp_error):
                        duplicate_stage = True

                    if debug:
                        print "OBSPY"
                        print other_out.stdout
                        print other_out.stderr
                        print xml_resp_error
            else:
                w = None

            if duplicate_stage is True:
                counter["duplicate_stage"] += 1
                print_warning("Faulty file. Duplicate Stage")
                continue

            # Parse the warning to determine if ObsPy raised a unit warning.
            unit_known_to_obspy = True
            if w:
                for msg in w:
                    message = msg.message.args[0]
                    if "The unit" in message and \
                            "not known to ObsPy" in message:
                        unit_known_to_obspy = False

            # Parse the stderr to figure out if evalresp raised a unit not
            # known error.
            if out and out.stderr and "are not supported" in out.stderr:
                unit_known_to_evalresp = False

            # Various unit errors.
            if unit_known_to_obspy is False and \
                    unit_known_to_evalresp is False:
                counter["evalresp_and_obsy_unit_error"] += 1
                counter["correct_responses"] += 1
                print_info("OK [Unit unknown to both]")
                continue
            elif unit_known_to_evalresp is False:
                counter["only_evalresp_unit_error"] += 1
                print_error("Only evalresp unit error!")
                continue
            elif unit_known_to_obspy is False:
                counter["only_obspy_unit_error"] += 1
                print_error("Only obspy unit error!")
                continue

            # If both fail it is ok.
            if seedresp_error:
                print_info("[OK] Evalresp failed to get response")
                counter["no_response_calculated_from_evalresp"] += 1
                continue
            # If only ObsPy fails then something needs to be done!
            elif xml_resp_error:
                print_error("The response extracted from the StationXML could "
                            "not be corrected but evalresp was able too...")
                print_error(str(xml_resp_error))
                counter["no_response_calculated_from_obspy"] += 1
                continue

            # Choose the first 1000 samples. Oftentimes numerically unstable
            # FIR filters which manifests most strongly in high frequencies.
            # And StationXML and RESP store numbers in a slightly different way
            # and thus rounding errors occur.
            seed_freq = seed_freq[:1000]
            xml_freq = xml_freq[:1000]
            seed_response = seed_response[:1000]
            xml_response = xml_response[:1000]

            # If both managed to calculate somthing, compare them!
            np.testing.assert_allclose(seed_freq, xml_freq, rtol=1E-6)
            try:
                np.testing.assert_allclose(seed_response, xml_response,
                                           rtol=1E-6)
            except Exception as e:
                if chan not in faulty_evalresp:
                    msg = "The responses are not identical!"
                    print_error(msg)
                    print_error(str(e))

                    #import matplotlib.pylab as plt
                    #plt.loglog(np.abs(seed_response), color="blue")
                    #plt.loglog(np.abs(xml_response), color="green")
                    #plt.show()

                    counter["faulty_responses"] += 1
                    continue

            print_good("[OK]")
            counter["correct_responses"] += 1

# Finally print some kind of report.
print "\n\n"
print 50 * "="
print 50 * "="
print "REPORT"
print 50 * "="

print_good("Correct responses: %i" % counter["correct_responses"])
print_error("Faulty responses: %i" % counter["faulty_responses"])

print_info("Responses evalresp failed to calculate: %i" %
           counter["no_response_calculated_from_evalresp"])
print_error("Responses only ObsPy failed to calculate: %i" %
            counter["no_response_calculated_from_obspy"])

print_good("Unit errors for both: %i" %
           counter["evalresp_and_obsy_unit_error"])
print_error("Unit errors only from ObsPy: %i" %
            counter["only_obspy_unit_error"])
print_error("Unit errors only from evalresp: %i" %
            counter["only_evalresp_unit_error"])

print_info("Unhandled polynomial responses: %i" %
           counter["polynomial_response"])

print_info("Evalresp segfaults: %i" % counter["evalresp_segfaults"])
print_warning("Files with duplicate stages: %i" % counter["duplicate_stage"])
print_error("Random errors: %i" % counter["random_error"])
