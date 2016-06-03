#!/bin/sh

cd qurancorpus
python setup.py register sdist bdist_egg upload
