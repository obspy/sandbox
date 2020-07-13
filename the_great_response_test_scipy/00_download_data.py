import obspy
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.header import URL_MAPPINGS

import pathlib

DATA_PATH = pathlib.Path("./data")
PROVIDERS = sorted(URL_MAPPINGS.keys())
NETWORK = None
STATION = None

# XXX: Overwritten here to only download a subset. For the full
# scale test just comment these lines.
PROVIDERS = ["IRIS"]
NETWORK = "IU"
STATION = "A*"


def download_stationxml_files_for_provider(
    provider: str, output_folder: pathlib.Path
) -> None:
    def _p(msg):
        print(f"Provider '{provider}': {msg}")

    output_folder.mkdir(exist_ok=True)

    # Get inventory for provider.
    client = Client(provider)
    _p("Retrieving inventory ...")
    try:
        inv = client.get_stations(
            level="station", format="text", network=NETWORK, station=STATION
        )
    except Exception as e:
        print(f"Failed to initialize client '{provider}' due to: {str(e)}")
        return
    _p("Done retrieving inventory ...")

    # Loop over all stations and retrieve the full response level dictionary.
    net_sta = []
    for network in inv:
        for station in network:
            net_sta.append((network.code, station.code))

    # Unique list to get rid of station epochs.
    net_sta = sorted(set(net_sta))

    for _i, (network, station) in enumerate(net_sta):
        filename = output_folder / f"{network}_{station}.xml"
        if filename.exists():
            _p(f"File '{filename} already exists.")
            continue
        _p(f"Downloading file {_i + 1} of {len(net_sta)}: {filename}")
        try:
            client.get_stations(
                network=network,
                station=station,
                level="response",
                filename=str(filename),
            )
        except Exception as e:
            _p(f"Failed to download '{filename}' due to: {str(e)}")
            continue


def main():
    for provider in PROVIDERS:
        download_stationxml_files_for_provider(
            provider=provider, output_folder=DATA_PATH
        )


if __name__ == "__main__":
    main()
