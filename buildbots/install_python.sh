#!/bin/bash
# Install a local environment suitable for building the ObsPy documentation

TARGET=$HOME/update-docs

if [ -e "$TARGET" ]
then
    echo "target exists, exiting"
    exit 1
fi

#######################
#######################

SRCDIR=$TARGET/src
mkdir -p $SRCDIR
cd $SRCDIR
wget 'http://www.python.org/ftp/python/2.7.3/Python-2.7.3.tgz'
wget 'http://nightly.ziade.org/distribute_setup.py'
wget 'http://heanet.dl.sourceforge.net/project/numpy/NumPy/1.6.2/numpy-1.6.2.tar.gz'
wget 'http://downloads.sourceforge.net/project/scipy/scipy/0.11.0/scipy-0.11.0.tar.gz'
wget 'http://downloads.sourceforge.net/project/matplotlib/matplotlib/matplotlib-1.1.0/matplotlib-1.1.0.tar.gz'
wget 'http://downloads.sourceforge.net/project/matplotlib/matplotlib-toolkits/basemap-1.0.5/basemap-1.0.5.tar.gz'

for FILE in Python-2.7.3.tgz numpy-1.6.2.tar.gz scipy-0.11.0.tar.gz matplotlib-1.1.0.tar.gz basemap-1.0.5.tar.gz
do
    tar -xf $FILE
done

cd $SRCDIR
cd Python-2.7.3/
./configure --prefix=$TARGET --enable-unicode=ucs4 && make && make install
export PATH=$TARGET/bin:$PATH

cd $SRCDIR
python distribute_setup.py

cd $SRCDIR
cd numpy-1.6.2/
python setup.py build --fcompiler=gnu95 && python setup.py install --prefix=$TARGET

cd $SRCDIR
cd scipy-0.11.0/
python setup.py install --prefix=$TARGET

cd $SRCDIR
cd matplotlib-1.1.0/
python setup.py build && python setup.py install --prefix=$TARGET

cd $SRCDIR
cd basemap-1.0.5/geos-3.3.3/
./configure --prefix=$TARGET && make && make install
cd ..
python setup.py install --prefix=$TARGET

easy_install pip
pip install sqlalchemy
pip install lxml
pip install ipython
pip install Cython
pip install suds
pip install hcluster
pip install http://downloads.sourceforge.net/project/mlpy/mlpy%203.5.0/mlpy-3.5.0.tar.gz

# for building ObsPy docs:
pip install Sphinx==1.1
pip install Pygments==1.4
pip install pep8==0.6.1
pip install Jinja2==2.6
pip install docutils==0.8.1
pip install coverage==3.5
