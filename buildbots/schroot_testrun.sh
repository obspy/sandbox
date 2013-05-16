#!/bin/bash
# Automated script to run tests in all schroot environments.
# schroot environments have to be set up accordingly beforehand.
# All dependencies for ObsPy have to be installed in the chroots.

DEBUNTUS="squeeze wheezy lucid natty oneiric precise quantal raring"
BASEDIR=/tmp/testrun
GITDIR=$BASEDIR/git
PYTHONDIR=$BASEDIR/python
LOG=$BASEDIR/log.txt
VIRTUALENV_PY=$BASEDIR/virtualenv.py
PIDFILE=$HOME/schroot_testrun.pid
MPLCONFIGDIR=$BASEDIR/.matplotlib

rm -rf $BASEDIR
mkdir -p $BASEDIR

# check if script is alread running
test -f $PIDFILE && echo "schroot test runner aborted: pid file exists" && exit 1
# otherwise create pid file
echo $! > $PIDFILE

# all output to log
exec > $LOG 2>&1

# end schroot session at end of script and remove pid file
function cleanup {
if [[ "$SCHROOT_SESSION" != "" ]]
then
    schroot -f --end-session -c "$SCHROOT_SESSION"
fi
rm -f $PIDFILE
}
trap cleanup EXIT


git clone https://github.com/obspy/obspy.git $GITDIR
wget -O $VIRTUALENV_PY 'https://raw.github.com/pypa/virtualenv/master/virtualenv.py'


for DIST in $DEBUNTUS
do
    for ARCH in i386 amd64
    do
        DISTARCH=${DIST}_${ARCH}
        echo "#### $DISTARCH"
        cd $GITDIR && git clean -fxd .
        rm $PYTHONDIR -rf
        rm $MPLCONFIGDIR -rf
        mkdir $MPLCONFIGDIR
        cd /tmp  # can make problems to enter schroot environment from a folder not present in the schroot
        SCHROOT_SESSION=$(schroot --begin-session -c $DISTARCH)
        schroot --run-session -c "$SCHROOT_SESSION" <<EOT
python $VIRTUALENV_PY --system-site-packages $PYTHONDIR
cd $GITDIR
export MPLCONFIGDIR=$MPLCONFIGDIR
$PYTHONDIR/bin/python setup.py develop -N -U --verbose
$PYTHONDIR/bin/python $GITDIR/obspy/core/scripts/runtests.py --all -r -n $DISTARCH
EOT
        schroot -f --end-session -c "$SCHROOT_SESSION" && SCHROOT_SESSION=""
    done
done
