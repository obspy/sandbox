#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Separate process to test for evalresp segfaults which otherwise interrupt the
current Python process.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2014
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""
from multiprocessing import Process
from obspy.signal.invsim import evalresp

from obspy.core.util.misc import CatchOutput

import sys


def test_evalresp_segfault(t_samp, filename, date, stat_id, chan_id, net_id,
                           loc_id, units):
        out = None
        try:
            with CatchOutput() as out:
                evalresp(
                    t_samp, 5, filename, date=date, station=stat_id,
                    channel=chan_id, network=net_id, locid=loc_id,
                    units=units, freq=True)
        except:
            if out and out.stderr and "are not supported" in out.stderr:
                sys.exit(99)
            else:
                sys.exit(1)


def test_for_segfault(t_samp, filename, date, stat_id, chan_id, net_id, loc_id,
                      units):

    p = Process(target=test_evalresp_segfault,
                args=(t_samp, filename, date, stat_id, chan_id, net_id,
                      loc_id, units))
    p.start()
    p.join()

    p.terminate()
    p.terminate()
    p.terminate()

    exitcode = p.exitcode
    filename.seek(0, 0)

    if exitcode and exitcode not in [1, 99]:
        return "segfault"
    elif exitcode == 1:
        return "Failed to calculate response"
    elif exitcode == 99:
        return "uniterror"
    else:
        return None
