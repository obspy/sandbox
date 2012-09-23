#!/bin/bash

CURDIR=/opt/obspy
PYTHONDIR=$CURDIR/python
SRCDIR=$CURDIR/python/src
TRUNK=$SRCDIR/obspy
PYTHON=$PYTHONDIR/bin/python
FTPUSER=obspy
FTPHOST=obspy.org
FTPPASSWD=fillinpasswordhere


cd $CURDIR


# check if script is alread running
test -f $CURDIR/update-docs.pid && exit

# otherwise create pid file
echo $! > $CURDIR/update-docs.pid

# remove existing python directory
rm -rf $PYTHONDIR

# unpack python.tgz
tar -xzf python.tgz

# update svn
#svn co https://svn.obspy.org/trunk -q $TRUNK &> $CURDIR/logs/svn.log
mkdir -p $SRCDIR
wget -O $SRCDIR/obspy.tgz https://github.com/obspy/obspy/tarball/master &> $CURDIR/logs/wget-git.log
tar -xz -C $SRCDIR -f $SRCDIR/obspy.tgz &> $CURDIR/logs/wget-git.log
mv $SRCDIR/obspy-obspy-* $TRUNK &> $CURDIR/logs/wget-git.log

# activate environment
source $PYTHONDIR/bin/activate

# run develop.sh
cd $TRUNK/misc/scripts
$TRUNK/misc/scripts/develop.sh &> $CURDIR/logs/develop.log
cd $CURDIR

# make docs
cd $TRUNK/misc/docs
make clean
make pep8 &> $CURDIR/logs/make_pep8.log
make coverage &> $CURDIR/logs/make_coverage.log
make html &> $CURDIR/logs/make_html.log
# make linkcheck &> $CURDIR/logs/make_linkcheck.log
# make doctest &> $CURDIR/logs/make_doctests.log
cd $CURDIR

# pack build directory
tar -czf $CURDIR/html.tgz -C $TRUNK/misc/docs/build/html .

# copy html.tgz to ObsPy server
ftp -n -v $FTPHOST &> $CURDIR/logs/ftp.log << EOT
ascii
user $FTPUSER $FTPPASSWD
prompt
put html.tgz
delete docs.tgz
rename html.tgz docs.tgz
bye
EOT

# report
obspy-runtests -r --all &> $CURDIR/logs/runtest.log

# delete pid file
rm -f $CURDIR/update-docs.pid
