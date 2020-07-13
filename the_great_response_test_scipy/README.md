# Brute-Force Response Test

This folder contains a collection of scripts to

(1) Download a large number of StationXML files.
(2) Compare the response calculation in evalresp to a new one in scipy.

The goal is to run this on a significant fraction of the data out there and
document any difference.

## Usage

First edit the script and then run it. By default it only downloads a fairly
small number of files - should be increased down the line.

```bash
python 00_download_data.py
```

Then run the tests on the downloaded files.

```bash
python 01_run_test.py
```

This will require a fair bit of manual work to get to work. The scripts are
designed in a way so they can be rerun and already performed work will be
skipped.
