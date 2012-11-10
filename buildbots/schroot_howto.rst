follow instructions on:
https://help.ubuntu.com/community/DebootstrapChroot

Install on Host
===============

Install packages::

    sudo aptitude install debootstrap schroot

In case of problems with forward compatibility download debootstrap package
from guest system or newer release::

    sudo aptitude install debootstrap -t testing

Configure schroot
=================

Setup Configuration files
-------------------------

Create one configuration per guest system, e.g.::

    sudo cat > /etc/schroot/chroot.d/lenny_i386.conf << EOF
    [lenny_i386]
    description=Debian 5.0 Lenny for i386
    directory=/srv/chroot/lenny_i386
    #personality=linux32
    root-users=megies
    #run-setup-scripts=true # deprecated
    #run-exec-scripts=true # deprecated
    type=directory
    users=megies
    EOF

Remove /home from mountpoints
-----------------------------

Per default the /home directory is mounted in the guest system, this should be
disabled::

    sudo vi /etc/schroot/mount-defaults

and change the corresponding line by commenting it out with a # sign::

    #/home           /home           none    rw,bind         0       0

Debootstrap the Guest Systems
=============================

Create directories and debootstrap them::

    sudo mkdir -p /srv/chroot/lenny_i386
    sudo mkdir -p /srv/chroot/lucid_i386
    sudo debootstrap --arch i386 --variant=buildd lenny /srv/chroot/lenny_i386 http://ftp.debian.org/debian/
    sudo debootstrap --arch i386 --variant=buildd --components=main,universe lucid /srv/chroot/lucid_i386/ http://archive.ubuntu.com/ubuntu/

Work in Guest System
====================

Issue the following commands if your user account is setup accordingly in the
schroot configuration above. For normal user access do::

    schroot -c lenny_i386

Or for root access do::

    schroot -c lenny_i386 -u root

To set up package building install (assuming option buildd in debootstrap) as root::

    apt-get install aptitude --no-install-recommends
    aptitude install python
    PYVERS=`pyversions -s`
    aptitude install vim-common $PYVERS python-setuptools python-support python-numpy lsb-release gfortran
    aptitude install ${PYVERS/ /-dev }-dev git fakeroot equivs lintian -R

Then build packages as normal user::

    git clone https://github.com/obspy/obspy.git /tmp/obspy
    cd /tmp/obspy/misc/debian/
    ./deb__build_debs.sh

Schroot can also run systems in background, see options "--start-session", "--run-session" and "--end-session".

Delete Guest System
===================

Check that no logins are present and no mounts are active! E.g. doing::

    mount | grep schroot
    schroot --all-sessions --list 

If necessary, end stale sessions, e.g.::

    schroot --all-sessions --end-session 

Then just delete the bootstrapped directory::

    sudo rm -rf /srv/chroot/lenny_i386
