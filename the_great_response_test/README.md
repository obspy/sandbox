# Testing the SEED/RESP -> obspy.core connection

Requires Python 3.6.

To use this, place any number of dataless SEED files in `./seed_files/*.seed`
and run

```bash
python run_response_test.py
```

For each SEED file found, it will:

1. Parse it to a parser object with `obspy.io.xseed`..
2. Get all the responses as RESP files.
3. Read the SEED file using `obspy.read_inventory()`.
4. Write it out as a StationXML file and validate the StationXML file.
5. Read it back again using `obspy.read_inventory()`.
6. For each channel and epoch it will (for DISP, VEL, ACC):
    a. Get the response from the RESP file using evalresp.
    b. Get it from the inventory object created by reading the SEED file.
    c. Get it from the inventory object created by reading the StationXML file.
    d. Create a new inventory object by using `obspy.read_inventory()` on the
       RESP file.
    e. Assert all 4 result in the same response!
7. If all tests pass it will move the SEED file to `./seed_files/success/`.


Doing this for a reasonable large selection of SEED files means we can be
pretty sure that ObsPy does the correct thing here.
