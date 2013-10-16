#!/bin/zsh
PYTHON=~/python332
PYTHONBIN=$PYTHON/bin/python3.3
export PYTHONPATH=..

rm -rf dist
rm -rf build

mkdir dist

$PYTHONBIN $PYTHON/Tools/freeze/freeze.py -X setproctitle -o build  kaa_freeze.py

cd build
make
cd ..
mv build/kaa_freeze.bin dist/kaa
cp ../README.rst dist/

find /Users/ishimoto/python332/lib -name '*.so' -exec cp {} dist/ \;
