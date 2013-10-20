#!/bin/zsh
# check issue 11824 and issue 16047 to use freeze.
PYTHON=~/src/cpython.kaa
PYTHONBIN=$PYTHON/bin/python3.3
export PYTHONPATH=..

rm -rf dist
rm -rf build

mkdir dist

$PYTHONBIN $PYTHON/Tools/freeze/freeze.py -m -X setproctitle -o build kaa_freeze.py kaa.filetype.html kaa.filetype.html.htmlmode  kaa.filetype.javascript kaa.filetype.javascript.javascriptmode  kaa.filetype.css kaa.filetype.css.cssmode  kaa.filetype.python kaa.filetype.python.pythonmode  

cd build
make
cd ..
mv build/kaa_freeze dist/kaa
cp ../README.rst dist/

find $PYTHON/lib -name '*.so' -exec cp {} dist/ \;
