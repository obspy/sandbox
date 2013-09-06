from obspy import read

filename = 'ZE.MS05..HHZ.D.2012.274'
st = read(filename)
respfile = 'RESP.ZE.MS05..HHZ'
seedresp = {'filename': respfile, 'date': st.traces[0].stats.starttime,
            'units': 'VEL'}
print st
st.simulate(paz_remove=None, seedresp=seedresp, taper=True,
            taper_fraction=0.005)
print st
