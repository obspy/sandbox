#!/bin/bash
# Install a local environment suitable for building the ObsPy documentation.
# Parts depend on globally installed packages (libxml, libxslt, libgeos ...) in
# certain version numbers.

TARGET=$HOME/python3

if [ -e "$TARGET" ]
then
    echo "target exists, exiting"
    exit 1
fi

#######################
#######################

export PKG_CONFIG_PATH=$TARGET/lib/pkgconfig
export LD_RUN_PATH=$TARGET/lib:$LD_RUN_PATH
export PATH=$TARGET/bin:$PATH
SRCDIR=$TARGET/src
mkdir -p $SRCDIR
# from now on all output to log file
LOG=$TARGET/build.log
exec > $LOG 2>&1

# download sources
cd $SRCDIR
wget 'https://www.python.org/ftp/python/3.3.5/Python-3.3.5.tgz'

# unpack sources
for FILE in *gz *bz2 *xz
do
    tar -xf $FILE
done

## build basic Python
cd $SRCDIR/Python-3.*
./configure --enable-shared --prefix=$TARGET && make && make install
if [ `which python3` != "$TARGET/bin/python3" ]; then exit 1; fi
cd $SRCDIR
wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O - | python3
easy_install-3.3 pip
pip3.3 install Cython

# build NumPy and SciPy
# NumPy < 1.7 does not compile with Python 3.3.0
pip3.3 install numpy>=1.8
pip3.3 install scipy>=0.13

# build matplotlib and basemap
pip3.3 install https://github.com/matplotlib/matplotlib/archive/v1.3.1.tar.gz
# basemap needs geos library and header files installed
# last stable version 1.0.7 does not build correctly against global libgeos on Debian,
# see https://github.com/matplotlib/basemap/pull/140
# on Debian wheezy install: libgeos-3.3.3 libgeos-c1 libgeos-dev
pip3.3 install https://github.com/matplotlib/basemap/archive/master.zip

# more ObsPy dependencies and useful stuff
pip3.3 install sqlalchemy
pip3.3 install lxml  # needs libxml and libxslt header packages
pip3.3 install readline
pip3.3 install ipython>=2.0
pip3.3 install suds-jurko
pip3.3 install future
pip3.3 install flake8
pip3.3 install nose
pip3.3 install mock
