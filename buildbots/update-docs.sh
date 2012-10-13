#!/bin/bash

# test command line arguments
if [ ! $# -eq 1 ] ; then
    echo "Usage: $0 master|stable"
    exit 1
fi
case $1 in
    master)
        TODO=master
        DOCSSUFFIX=""
        ;;
    stable)
        TODO=stable
        DOCSSUFFIX="_stable"
        ;;
    *) echo "Usage: $0 master|stable"; exit 1 ;;
esac


BASEDIR=$HOME/update-docs/$TODO
LOGDIR=$BASEDIR/logs
PYTHONDIR=$BASEDIR/python
PYTHONTGZ=$HOME/python.tgz
SRCDIR=$BASEDIR/python/src
GITDIR=$SRCDIR/obspy
PYTHON=$PYTHONDIR/bin/python
FTPUSER=obspy
FTPHOST=obspy.org
FTPPASSWD=fillinpasswordhere
PIDFILE=$BASEDIR/${TODO}.pid


mkdir -p $BASEDIR
mkdir -p $LOGDIR


# check if script is alread running
test -f $PIDFILE && exit
# otherwise create pid file
echo $! > $PIDFILE

# remove existing python directory
rm -rf $PYTHONDIR
# unpack python.tgz
cd $BASEDIR
ln -s $PYTHONTGZ python.tgz
tar -xzf python.tgz

# clone github repository
git clone https://github.com/obspy/obspy.git $GITDIR &> $LOGDIR/git.log

# checkout the state we want to work on (last stable tag / master)
case $TODO in
    master)
        git checkout master
        ;;
    stable)
        STABLE=`git tag | tail -1`
        git checkout $STABLE
        ;;
esac

# activate environment
source $PYTHONDIR/bin/activate

# run develop.sh
cd $GITDIR/misc/scripts
./develop.sh &> $LOGDIR/develop.log

# make docs
cd $GITDIR/misc/docs
make clean
make pep8 &> $LOGDIR/make_pep8.log
make coverage &> $LOGDIR/make_coverage.log
make html &> $LOGDIR/make_html.log
# make linkcheck &> $LOGDIR/make_linkcheck.log
# make doctest &> $LOGDIR/make_doctests.log

# pack build directory
tar -czf $BASEDIR/html${DOCSSUFFIX}.tgz -C $GITDIR/misc/docs/build/html .

# copy html.tgz to ObsPy server
cd $BASEDIR
ftp -n -v $FTPHOST &> $LOGDIR/ftp.log << EOT
ascii
user $FTPUSER $FTPPASSWD
prompt
put html${DOCSSUFFIX}.tgz
delete docs${DOCSSUFFIX}.tgz
rename html${DOCSSUFFIX}.tgz docs${DOCSSUFFIX}.tgz
bye
EOT

# report
obspy-runtests -r --all &> $LOGDIR/runtest.log

# delete pid file
rm -f $PIDFILE
