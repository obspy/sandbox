#!/bin/bash

CURDIR=/opt/obspy
PYTHONDIR=$CURDIR/python_stable
TRUNK=$PYTHONDIR/src/obspy
DOCSDIR=$TRUNK/misc/docs
PYTHON=$PYTHONDIR/bin/python
FTPUSER=obspy
FTPHOST=obspy.org
FTPPASSWD=fillinpasswordhere


cd $CURDIR


# check if script is alread running
test -f $CURDIR/update-docs_stable.pid && exit

# otherwise create pid file
echo $! > $CURDIR/update-docs_stable.pid

# remove existing python directory
rm -rf $PYTHONDIR
mkdir $PYTHONDIR

# unpack python.tgz
tar -xzf python.tgz -C $PYTHONDIR
mv $PYTHONDIR/python/* $PYTHONDIR
rm $PYTHONDIR/python -r

# activate environment
source $PYTHONDIR/bin/activate

# run develop.sh
for PACKAGE in core arclink datamark db earthworm events gse2 imaging iris mseed neries realtime sac seedlink seg2 segy seisan seishub sh signal taup wav xseed
    do
    easy_install obspy.${PACKAGE} &> $CURDIR/logs/install_stable.log
    done
cd $CURDIR

# update svn
#svn -q --non-interactive co https://svn.obspy.org/trunk -q $TRUNK
svn co https://svn.obspy.org/trunk/misc/docs -q $DOCSDIR &> $CURDIR/logs/svn_stable.log

# make docs
cd $DOCSDIR
make clean
make pep8 &> $CURDIR/logs/make_pep8_stable.log
make coverage &> $CURDIR/logs/make_coverage_stable.log
make html &> $CURDIR/logs/make_html_stable.log
# make linkcheck &> $CURDIR/logs/make_linkcheck.log
# make doctest &> $CURDIR/logs/make_doctests.log
cd $CURDIR

# pack build directory
tar -czf $CURDIR/html_stable.tgz -C $DOCSDIR/build/html .

# copy html.tgz to ObsPy server
ftp -n -v $FTPHOST &> $CURDIR/logs/ftp.log << EOT
ascii
user $FTPUSER $FTPPASSWD
prompt
put html_stable.tgz
delete docs_stable.tgz
rename html_stable.tgz docs_stable.tgz
bye
EOT

# report
obspy-runtests -r --all &> $CURDIR/logs/runtest_stable.log

# delete pid file
rm -f $CURDIR/update-docs_stable.pid
