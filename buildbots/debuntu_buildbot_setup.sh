#!/bin/bash
# this script *should* work without problems but is better run interactively
# line by line (package names changing for different distros, etc.)
echo "check contents before running this script."
exit 1

ARCHS="i386 amd64"
DEBIANS="squeeze wheezy"
UBUNTUS="lucid natty oneiric precise quantal raring"

# add testing to sources.list, we need a more recent debootstrap that knows
# the more recent ubuntu releases...
sudo cat >> /etc/apt/sources.list <<'EOT'

deb http://ftp.de.debian.org/debian/ testing main # REMOVE AGAIN
EOT
sudo aptitude update
sudo aptitude install debootstrap -t testing
# remove our sources.list entry again, otherwise aptitude wants to update
# all our packages...
sudo ex /etc/apt/sources.list <<'EOT'
g/REMOVE AGAIN/d
wq
EOT
sudo aptitude update
sudo aptitude install schroot

# comment out line that mounts /home in schroot:
sudo ex /etc/schroot/mount-defaults <<'EOT'
g/^\/home/s/^/#/
wq
EOT

# make the config files for schroot
sudo cat > /etc/schroot/chroot.d/squeeze_i386.conf << EOT
[squeeze_i386]
description=Debian 6.0 Squeeze for i386
directory=/srv/chroot/squeeze_i386
root-users=root
type=directory
users=obspy
EOT
sudo cat > /etc/schroot/chroot.d/squeeze_amd64.conf << EOT
[squeeze_amd64]
description=Debian 6.0 Squeeze for amd64
directory=/srv/chroot/squeeze_amd64
root-users=root
type=directory
users=obspy
EOT
sudo cat > /etc/schroot/chroot.d/wheezy_i386.conf << EOT
[wheezy_i386]
description=Debian 7.0 Wheezy for i386
directory=/srv/chroot/wheezy_i386
root-users=root
type=directory
users=obspy
EOT
sudo cat > /etc/schroot/chroot.d/wheezy_amd64.conf << EOT
[wheezy_amd64]
description=Debian 7.0 Wheezy for amd64
directory=/srv/chroot/wheezy_amd64
root-users=root
type=directory
users=obspy
EOT
sudo cat > /etc/schroot/chroot.d/lucid_i386.conf << EOT
[lucid_i386]
description=Ubuntu 10.04 LTS Lucid Lynx for i386
directory=/srv/chroot/lucid_i386
root-users=root
type=directory
users=obspy
EOT
sudo cat > /etc/schroot/chroot.d/lucid_amd64.conf << EOT
[lucid_amd64]
description=Ubuntu 10.04 LTS Lucid Lynx for amd64
directory=/srv/chroot/lucid_amd64
root-users=root
type=directory
users=obspy
EOT
sudo cat > /etc/schroot/chroot.d/natty_i386.conf << EOT
[natty_i386]
description=Ubuntu 11.04 Natty Narwhal for i386
directory=/srv/chroot/natty_i386
root-users=root
type=directory
users=obspy
EOT
sudo cat > /etc/schroot/chroot.d/natty_amd64.conf << EOT
[natty_amd64]
description=Ubuntu 11.04 Natty Narwhal for amd64
directory=/srv/chroot/natty_amd64
root-users=root
type=directory
users=obspy
EOT
sudo cat > /etc/schroot/chroot.d/oneiric_i386.conf << EOT
[oneiric_i386]
description=Ubuntu 11.10 Oneiric Ocelot for i386
directory=/srv/chroot/oneiric_i386
root-users=root
type=directory
users=obspy
EOT
sudo cat > /etc/schroot/chroot.d/oneiric_amd64.conf << EOT
[oneiric_amd64]
description=Ubuntu 11.10 Oneiric Ocelot for amd64
directory=/srv/chroot/oneiric_amd64
root-users=root
type=directory
users=obspy
EOT
sudo cat > /etc/schroot/chroot.d/precise_i386.conf << EOT
[precise_i386]
description=Ubuntu 12.04 LTS Precise Pangolin for i386
directory=/srv/chroot/precise_i386
root-users=root
type=directory
users=obspy
EOT
sudo cat > /etc/schroot/chroot.d/precise_amd64.conf << EOT
[precise_amd64]
description=Ubuntu 12.04 LTS Precise Pangolin for amd64
directory=/srv/chroot/precise_amd64
root-users=root
type=directory
users=obspy
EOT
sudo cat > /etc/schroot/chroot.d/quantal_i386.conf << EOT
[quantal_i386]
description=Ubuntu 12.10 Quantal Quetzal for i386
directory=/srv/chroot/quantal_i386
root-users=root
type=directory
users=obspy
EOT
sudo cat > /etc/schroot/chroot.d/quantal_amd64.conf << EOT
[quantal_amd64]
description=Ubuntu 12.10 Quantal Quetzal for amd64
directory=/srv/chroot/quantal_amd64
root-users=root
type=directory
users=obspy
EOT
sudo cat > /etc/schroot/chroot.d/raring_i386.conf << EOT
[raring_i386]
description=Ubuntu 13.04 Raring Ringtail for i386
directory=/srv/chroot/raring_i386
root-users=root
type=directory
users=obspy
EOT
sudo cat > /etc/schroot/chroot.d/raring_amd64.conf << EOT
[raring_amd64]
description=Ubuntu 13.04 Raring Ringtail for amd64
directory=/srv/chroot/raring_amd64
root-users=root
type=directory
users=obspy
EOT

# debootstrap all currently supported debian/ubuntu distros
# this takes ~500MB per distro and architecture (after all additional installs later)
for ARCH in $ARCHS
do
    for DISTRO in $DEBIANS
    do
        DIR=/srv/chroot/${DISTRO}_${ARCH}
        sudo mkdir -p $DIR
        sudo debootstrap --arch $ARCH --variant=buildd $DISTRO $DIR http://ftp.debian.org/debian/
    done
done
for ARCH in $ARCHS
do
    for DISTRO in $UBUNTUS
    do
        DIR=/srv/chroot/${DISTRO}_${ARCH}
        sudo mkdir -p $DIR
        sudo debootstrap --arch $ARCH --variant=buildd --components=main,universe $DISTRO $DIR http://archive.ubuntu.com/ubuntu/
    done
done

# install additional packages necessary for building the deb files
for ARCH in $ARCHS
do
    for DISTRO in $DEBIANS $UBUNTUS
    do
sudo cat <<'EOT'| schroot -c ${DISTRO}_${ARCH} -u root
apt-get install aptitude --no-install-recommends
aptitude install python
PYVERS=`pyversions -s`
aptitude install vim-common $PYVERS python-setuptools python-support python-numpy python-scipy lsb-release gfortran python-lxml python-matplotlib python-sqlalchemy python-suds
aptitude install ${PYVERS/ /-dev }-dev git fakeroot equivs lintian -R
exit
EOT
    done
done
