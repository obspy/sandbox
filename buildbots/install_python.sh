#!/bin/bash
# Install a local environment suitable for building the ObsPy documentation.
# Parts depend on globally installed packages (gtk+, Qt, libxml, ...) in
# certain version numbers (Debian Squeeze).

TARGET=$HOME/local

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
wget 'http://www.python.org/ftp/python/2.7.5/Python-2.7.5.tgz'
wget 'http://nightly.ziade.org/distribute_setup.py'
wget 'http://heanet.dl.sourceforge.net/project/numpy/NumPy/1.7.1/numpy-1.7.1.tar.gz'
wget 'http://downloads.sourceforge.net/project/scipy/scipy/0.12.0/scipy-0.12.0.tar.gz'
wget 'http://downloads.sourceforge.net/project/matplotlib/matplotlib-toolkits/basemap-1.0.7/basemap-1.0.7.tar.gz'
wget 'http://ftp.gnome.org/pub/gnome/sources/gobject-introspection/0.10/gobject-introspection-0.10.8.tar.bz2'
wget 'http://www.cairographics.org/releases/py2cairo-1.8.10.tar.gz'
wget 'http://ftp.acc.umu.se/pub/gnome/sources/pygobject/2.21/pygobject-2.21.5.tar.bz2'
wget 'http://ftp.gnome.org/pub/GNOME/sources/pygtk/2.17/pygtk-2.17.0.tar.bz2'
wget 'http://sourceforge.net/projects/pyqt/files/sip/sip-4.14.1/sip-4.14.1.tar.gz'
wget 'http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.9.5/PyQt-x11-gpl-4.9.5.tar.gz'

# unpack sources
for FILE in *gz *bz2 *xz
do
    tar -xf $FILE
done

# build basic Python
cd $SRCDIR/Python-*
./configure --enable-shared --prefix=$TARGET --enable-unicode=ucs4 && make && make install || exit 1
if [ `which python` != "$TARGET/bin/python" ]; then exit 1; fi
cd $SRCDIR
python distribute_setup.py
easy_install pip
pip install Cython

# build NumPy and SciPy
cd $SRCDIR/numpy-*
python setup.py build --fcompiler=gnu95 && python setup.py install --prefix=$TARGET
cd $SRCDIR/scipy-*
python setup.py install --prefix=$TARGET

# build GTK bindings (for matplotlib backend)
cd $SRCDIR/gobject-introspection-0.10.8
./configure --prefix=$TARGET && make && make install
cd $SRCDIR/pycairo-1.8.10
./waf configure --prefix=$TARGET && ./waf build && ./waf install
cd $SRCDIR/pygobject-2.21.5
./configure --prefix=$TARGET && make && make install
cd $SRCDIR/pygtk-2.17.0
./configure --prefix=$TARGET && make && make install

# build Qt bindings, PyQt and pyside (for matplotlib backend)
cd $SRCDIR/sip-4.14.1
python configure.py && make && make install
cd $SRCDIR/PyQt-x11-gpl-4.9.5
echo 'yes' | python configure.py && make && make install
pip install pyside

# build matplotlib and basemap
pip install https://github.com/matplotlib/matplotlib/archive/v1.3.x.zip
cd $SRCDIR/basemap-*/geos-*
./configure --prefix=$TARGET && make && make install
export GEOS_DIR=$TARGET
cd $SRCDIR/basemap-*
python setup.py install --prefix=$TARGET

# more ObsPy dependencies and useful stuff
pip install sqlalchemy
pip install lxml
pip install pysqlite
pip install readline
pip install ipython
pip install suds
pip install hcluster
pip install pyproj
pip install http://downloads.sourceforge.net/project/mlpy/mlpy%203.5.0/mlpy-3.5.0.tar.gz

# for building ObsPy docs:
pip install Sphinx==1.1
pip install Pygments==1.4
pip install pep8==0.6.1
pip install Jinja2==2.6
pip install docutils==0.8.1
pip install coverage==3.5
pip install flake8

# for running SeisHub:
pip install Markdown==2.0.3
pip install Cheetah==2.4.4
pip install pyasn1==0.1.3
pip install pycrypto==2.6
pip install pyOpenSSL==0.13
pip install psycopg2==2.4.5
pip install zope.interface==4.0.1
pip install Twisted==12.1.0
pip install pyparsing
