# StationXML Test Case

This folder contains the test case for the evalresp integration in ObsPy.

The following is a short description of the files.

* **download_all_stations.py**: Downloads the StationXML files at the response
  level from IRIS. It requires an `all_stations.xml` file, a station level
  StationXML file which has to be downloaded separately.
* **convert_to_SEED.sh**: Bash script converting all StationXML files to SEED
  using the Java tool by IRIS.
* **evresp_process.py**: Running evalresp in a separate process to test whether
  it segfaults or not. Otherwise it would crash the current Python process.

* **test_response_large_scale.py**: The actual test case. It loops over every
  StationXML file in the *StationXML* subfolder and calculates the response for
  each channel using the ObsPy to evalresp bridge. These responses are compared
  to responses calculate by converting the SEED files in the *SEED* subfolder
  to RESP files and directly using evalresp with them.
