import pathlib

import matplotlib.pyplot as plt
import numpy as np
import obspy
from obspy.core.inventory.response import Response

CACHE_PATH = pathlib.Path("./cache")
DATA_PATH = pathlib.Path("./data")

# Number of frequencies to test at.
N_FREQUENCIES = 100

# TOLERANCES
RTOL = 1e-4
ATOL_AS_FRAC_OF_ABS_MAX = 5e-4

# Collect phase responses here that don't compare favourable to evalresp
# but which have been manually verified to be at least as correct in the
# new scipy implementation.
# This will have to be expanded in the course of this test.
SKIP_VALIDATING_PHASE_REPONSE = ["IU.AFI..UHE", "IU.AFI..UHN", "IU.AFI..UHZ"]


def compare_single_response(channel_id: str, response: Response):
    # detect sampling rate from response stages
    for stage in response.response_stages[::-1]:
        if (
            stage.decimation_input_sample_rate is not None
            and stage.decimation_factor is not None
        ):
            sampling_rate = stage.decimation_input_sample_rate / stage.decimation_factor
            break
    else:
        # XXX: Something has to be done here.
        msg = "Failed to autodetect sampling rate of channel from " "response stages."
        raise Exception(msg)

    # Compute up to the Nyquist frequency - evalresp's phase usually goes crazy
    # afterwards.
    FREQUENCIES = np.logspace(-2, np.log10(0.5 * sampling_rate), N_FREQUENCIES)

    # Compute for evalresp as well as the scipy response.
    try:
        eval_resp = response.get_evalresp_response_for_frequencies(
            FREQUENCIES, output="VEL"
        )
    except Exception as e:
        print(
            "  evalresp failed to compute response. Thus no comparision can be"
            f"performed. Reason for evalresp failure: {str(e)}"
        )
        return

    scipy_resp = response.get_response(FREQUENCIES, output="VEL")

    # Use amplitude and phase for the comparison just because it is more
    # intuitive.
    eval_resp_amplitude = np.abs(eval_resp)
    eval_resp_phase = np.angle(eval_resp)

    scipy_resp_amplitude = np.abs(scipy_resp)
    scipy_resp_phase = np.angle(scipy_resp)

    atol_amplitude = scipy_resp_amplitude.max() * ATOL_AS_FRAC_OF_ABS_MAX
    atol_phase = np.abs(scipy_resp_phase).max() * ATOL_AS_FRAC_OF_ABS_MAX

    try:
        np.testing.assert_allclose(
            eval_resp_amplitude,
            scipy_resp_amplitude,
            rtol=RTOL,
            atol=atol_amplitude,
            err_msg="amplitude mismatch",
        )
        # Skip if manually verified.
        if channel_id not in SKIP_VALIDATING_PHASE_REPONSE:
            np.testing.assert_allclose(
                eval_resp_phase,
                scipy_resp_phase,
                rtol=RTOL,
                atol=atol_phase,
                err_msg="amplitude mismatch",
            )
    except Exception as e:
        print(f"Failed comparison due to: {str(e)}")
        print("Will now produce a plot to help diagnose the issue.")

        plt.subplot(411)
        plt.title("Amplitude response")
        plt.loglog(FREQUENCIES, eval_resp_amplitude, label="Evalresp")
        plt.loglog(FREQUENCIES, scipy_resp_amplitude, label="scipy")
        plt.legend()

        plt.subplot(412)
        plt.title("Amplitude response difference")
        plt.loglog(FREQUENCIES, eval_resp_amplitude - scipy_resp_amplitude)

        plt.subplot(413)
        plt.title("Phase response")
        plt.semilogx(FREQUENCIES, eval_resp_phase, label="Evalresp")
        plt.semilogx(FREQUENCIES, scipy_resp_phase, label="scipy")
        plt.legend()

        plt.title("Phase response difference")
        plt.subplot(414)
        plt.semilogx(FREQUENCIES, eval_resp_phase - scipy_resp_phase)

        plt.show()
        raise e


def test_single_stationxml_file(filename: pathlib.Path):
    def _p(msg, indent: int = 0):
        print(f"{' ' * indent}File '{filename}': {msg}")

    # Simplistic cache to be able to rerun this a lot and fix
    # bugs as they appear.
    cache_file = CACHE_PATH / filename.name
    if cache_file.exists():
        _p("Already has been tested. Skipping ...", indent=2)
        return

    try:
        inv = obspy.read_inventory(str(filename))
    except Exception as e:
        _p(f"Failed to parse due to: {str(e)}")
        raise e

    all_responses = []
    for net in inv:
        for sta in net:
            for cha in sta:
                all_responses.append(
                    [
                        net.code,
                        sta.code,
                        cha.location_code,
                        cha.code,
                        cha.start_date,
                        cha.end_date,
                        cha.response,
                    ]
                )
    for _i, c in enumerate(all_responses):
        _p(f"Comparing responses for {c[:-1]} ...", indent=2)
        compare_single_response(channel_id=".".join(c[:4]), response=c[-1])

    # Finally just touch the cache file so it will be skipped the next run.
    cache_file.touch()


def main():
    CACHE_PATH.mkdir(exist_ok=True)
    all_files = list(DATA_PATH.glob("*.xml"))
    for _i, filename in enumerate(all_files):
        print(f"Reading StationXML file {_i + 1} of {len(all_files)}: {filename}")
        test_single_stationxml_file(filename)


if __name__ == "__main__":
    main()
