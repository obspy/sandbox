#!/bin/bash

USAGE="Usage: $0 master|stable"

# test command line arguments
if [ ! $# -eq 1 ] ; then
    echo $USAGE
    exit 1
fi
case $1 in
    master)
        DOCSSUFFIX=""
        ;;
    stable)
        DOCSSUFFIX="_stable"
        ;;
    *)
        echo $USAGE
        exit 1
        ;;
esac


BASEDIR=$HOME/update-docs
LOG=$BASEDIR/log.txt
TGZ=$HOME/update-docs.tgz
GITDIR=$BASEDIR/src/obspy
FTPUSER=obspy
FTPHOST=obspy.org
FTPPASSWD=fillinpasswordhere
PIDFILE=$BASEDIR/update-docs.pid

# clean directory
rm -rf $BASEDIR
mkdir -p $BASEDIR

# check if script is alread running
test -f $PIDFILE && echo "doc building aborted: pid file exists" && exit 1
# otherwise create pid file
echo $! > $PIDFILE

# from now on all output to log file
exec > $LOG 2>&1

# set trap to remove pid file after exit of script
function cleanup {
rm -f $PIDFILE
}
trap cleanup EXIT
# unpack basedir
cd $HOME
tar -xzf $TGZ

# clone github repository
git clone https://github.com/obspy/obspy.git $GITDIR

# checkout the state we want to work on (last stable tag / master)
cd $GITDIR
case $1 in
    master)
        git checkout master
        ;;
    stable)
        STABLE=`git tag | tail -1`
        git checkout $STABLE
        ;;
esac

# use unpacked python
export PATH=$BASEDIR/bin:$PATH

# run develop.sh
cd $GITDIR
$BASEDIR/bin/python setup.py develop -N -U --verbose

# make docs
cd $GITDIR/misc/docs
make clean
# works with pep8==0.6.1 but not pep8==1.3.3 (parts were refactored into an OO approach)
make pep8
# works with coverage==3.5 but not current coverage
make coverage
make html
make latexpdf
# make linkcheck
# make doctest
make c_coverage

# pack build directory
ln $LOG $GITDIR/misc/docs/build/html
tar -czf $BASEDIR/html${DOCSSUFFIX}.tgz -C $GITDIR/misc/docs/build/html .

# copy html.tgz to ObsPy server
cd $BASEDIR
ftp -n -v $FTPHOST << EOT
ascii
user $FTPUSER $FTPPASSWD
prompt
put html${DOCSSUFFIX}.tgz
delete docs${DOCSSUFFIX}.tgz
rename html${DOCSSUFFIX}.tgz docs${DOCSSUFFIX}.tgz
put $GITDIR/misc/docs/build/latex/ObsPyTutorial.pdf
bye
EOT

# report
$BASEDIR/bin/obspy-runtests -r --all
exit 0
