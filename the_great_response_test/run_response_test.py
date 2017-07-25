import collections
import os
import pathlib
import time
import shutil
import warnings

import numpy as np
import tqdm

import obspy
from obspy.io.xseed import Parser
from obspy.core.util.testing import NamedTemporaryFile
from obspy.signal.invsim import evalresp_for_frequencies

# Directory with SEED files.
data_dir = pathlib.Path(__file__).parent / "seed_files"

# Directory where SEED files will be copied if all tests pass for it.
success_dir = data_dir / "success"
if not success_dir.exists():
    os.makedirs(success_dir)

# Sort the SEED files by size to first test a larger variety of files.
files = sorted(list(data_dir.glob("*dataless")),
               key=lambda x: x.stat().st_size)

# Directory where temporary files live.
work_dir = pathlib.Path(__file__).parent / "work_dir"
if not work_dir.exists():
    os.makedirs(work_dir)

# Invalid responses are automatically skipped.
SKIP_INVALID_RESPONSES = True

counter = 0

for filename in files:
    print("=================================")
    print(f"FILENAME: {filename}")
    print("=================================")

    # Parse it with the existing ObsPy Parser object.
    a = time.time()
    parser = Parser(str(filename))
    b = time.time()
    print(f"Time for parsing SEED file with obspy.io.xseed: {b -a}")

    # Create RESP files.
    a = time.time()
    resp_files = {_i[0]: _i[1] for _i in parser.get_resp()}
    b = time.time()
    print(f"Time for writing RESP files: {b - a}")

    # Parse it with the read_inventory() function.
    a = time.time()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        inv_from_seed = obspy.read_inventory(
            str(filename),
            skip_invalid_responses=SKIP_INVALID_RESPONSES)

    # Some files specify an azimuth of 360.0 degrees which is not valid in the
    # StationXML schema and thus should be changed to zero.
    for net in inv_from_seed:
        for sta in net:
            for cha in sta:
                if not hasattr(cha, "azimuth"):
                    continue
                if cha.azimuth == 360.0:
                    cha.azimuth = 0.0

    # Figure out if to validate or not to validate the StationXML - basically
    # try to find if Blockette 58 exists everywhere or not and if all units
    # could be resolved.
    validate = True
    for _w in w:
        if "does not end with blockette 58" in str(_w) or \
                "abbreviation" in str(_w).lower():
            validate = False
            break
    # Don't validate if blockette 62 is preset. On stage 0 it must not have a
    # blockette 58 and it also does not have one in many other cases. This
    # cannot result in a valid StationXML file unfortunately.
    if 62 in parser.blockettes and parser.blockettes[62]:
        validate = False

    print(f"Validate StationXML: {validate}")
    b = time.time()
    print(f"Time for parsing SEED File to inventory object: {b - a}")

    # Write it out as StationXML and validate it (if possible)...
    a = time.time()
    inv_from_seed.write(str(work_dir / "tmp.xml"), format="stationxml",
                        validate=validate)
    b = time.time()
    print(f"Time to write and validate StationXML: {b - a}")

    # Read again.
    a = time.time()
    inv_from_xml = obspy.read_inventory(str(work_dir / "tmp.xml"))
    b = time.time()
    print(f"Time to read StationXML: {b - a}")

    # Get all the channels and epochs - get it from the SEED files as it is
    # likely the most complete.
    channels = collections.defaultdict(list)
    for c in parser.get_inventory()["channels"]:
        channels[c["channel_id"]].append(
            (c["start_date"], c["end_date"]))

    # Loop over each channel.
    for channel, epochs in tqdm.tqdm(channels.items()):
        with NamedTemporaryFile() as tf:
            # Write the corresponding RESP file.
            r = resp_files["RESP.%s" % channel]
            r.seek(0, 0)
            tf.write(r.read())

            # Now loop over the epochs.
            for start, end in epochs:
                # Get the time to ask for.
                if end:
                    t = start + (end - start) / 2
                else:
                    t = start + 10

                net, sta, loc, cha = channel.split(".")

                # Find the response in the inventory read from the SEED file.
                _inv_t = inv_from_seed.select(network=net, station=sta,
                                              location=loc, channel=cha,
                                              starttime=t - 1, endtime=t + 1)
                # Should now only be a single channel.
                try:
                    assert _inv_t.get_contents()["channels"] == [channel]
                except AssertionError:
                    msg = ("`inv.select()` did not work as expected. This is "
                           "likely because the start-and end dates in one of "
                           "the files is wrong. Please fix it and run again. "
                           "This channel will be skipped.")
                    print(msg)
                    continue
                response_from_seed = _inv_t[0][0][0].response
                # Log channels don't really have a response - skip them.
                if response_from_seed is None and cha == "LOG":
                    continue
                _inv_xml_t = inv_from_xml.select(network=net, station=sta,
                                                 location=loc, channel=cha,
                                                 starttime=t - 1, endtime=t + 1)
                assert _inv_xml_t.get_contents()["channels"] == [channel]
                response_from_stationxml = _inv_xml_t[0][0][0].response

                # Get the Nyquist frequency of the channel.
                if hasattr(_inv_xml_t[0][0][0], "sample_rate"):
                    nyquist = _inv_xml_t[0][0][0].sample_rate / 2.0
                else:
                    nyquist = 1000.0

                # Only compare up to Nyquist as algorithms can get pretty
                # unstable afterwards and they are sensitive to very small
                # changes in later decimal digits which are unavoidable when
                # converting between formats.
                frequencies = np.logspace(-3, np.log10(nyquist), 100)

                # Don't compare the response list stages as we handle them a
                # bit differently from evalresp - but this is tested elsewhere
                # in ObsPy's test suite.
                if response_from_seed and "ResponseListResponseStage" in [
                        _i.__class__.__name__
                        for _i in response_from_seed.response_stages]:
                    continue

                # Skip gain only responses as evalresp does some weird things
                # with those which I don't really understand. I mean these
                # should just be flat and real after all.
                if response_from_seed and \
                        not response_from_seed.response_stages:
                    print("No response stages - just stage 0 - "
                          "will be skipped.")
                    continue

                # Loop over all units.
                for unit in ("DISP", "VEL", "ACC"):
                    # First try evalresp - if it does not work just go to the
                    # next epoch. The reasoning is that we want to make sure
                    # that our responses (calculated no matter which way) are
                    # equal to evalresp.
                    try:
                        r_evalresp = evalresp_for_frequencies(
                            t_samp=None, frequencies=frequencies,
                            filename=tf.name, date=t, units=unit)
                    except:
                        continue

                    # Get response from SEED file.
                    try:
                        r_seed = response_from_seed\
                            .get_evalresp_response_for_frequencies(
                                frequencies=frequencies, output=unit)
                    except Exception as e:
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                        print(e)
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                        import pdb; pdb.set_trace()

                    # Get response from the StationXML file.
                    try:
                        r_stationxml = response_from_stationxml\
                            .get_evalresp_response_for_frequencies(
                                frequencies=frequencies, output=unit)
                    except Exception as e:
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                        print(e)
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                        import pdb; pdb.set_trace()

                    # Last but not least, also read the RESP file with
                    # obspy.core
                    try:
                        r_resp_obspy = obspy.read_inventory(tf.name).select(
                            starttime=t - 1,
                            endtime=t + 1)[0][0][0].response\
                            .get_evalresp_response_for_frequencies(
                            frequencies=frequencies, output=unit)
                    except Exception as e:
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                        print(e)
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                        import pdb; pdb.set_trace()


                    # Convert NaNs and infs to actual numbers both on the real
                    # as well as the complex part. We again want to assert that
                    # all responses are equal to what evalresp would do so
                    # this should be safe enought.
                    r_evalresp.real = np.nan_to_num(r_evalresp.real)
                    r_evalresp.imag = np.nan_to_num(r_evalresp.imag)
                    r_seed.real = np.nan_to_num(r_seed.real)
                    r_seed.imag = np.nan_to_num(r_seed.imag)
                    r_stationxml.real = np.nan_to_num(r_stationxml.real)
                    r_stationxml.imag = np.nan_to_num(r_stationxml.imag)
                    r_resp_obspy.real = np.nan_to_num(r_resp_obspy.real)
                    r_resp_obspy.imag = np.nan_to_num(r_resp_obspy.imag)


                    # Adaptive absolute tolerance to deal with very
                    # small values.
                    atol = 1E-5 * max(np.abs(r_evalresp.real).max(),
                                      np.abs(r_evalresp.imag).max())

                    cases = [(r_seed, "SEED file"),
                             (r_stationxml, "StationXML file"),
                             (r_resp_obspy, "RESP file with ObsPy")]

                    for c, msg in cases:
                        try:
                            np.testing.assert_allclose(
                                r_evalresp.real,
                                c.real,
                                rtol=1E-6, atol=atol)
                        except Exception as e:
                            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                            print(f"{msg}, real")
                            print(e)
                            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                            import pdb; pdb.set_trace()
                        try:
                            np.testing.assert_allclose(
                                r_evalresp.imag,
                                c.imag,
                                rtol=1E-6, atol=atol)
                        except Exception as e:
                            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                            print(f"{msg}, imag")
                            print(e)
                            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                            import pdb; pdb.set_trace()

                    counter += 1

    print(f"Successfully tested {counter} responses for equality!!")
    # Move to success folder.
    shutil.move(filename, success_dir / filename.name)
