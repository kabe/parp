#!/bin/sh

pep8 test.py
pep8 TauLoad/Loader.py
pep8 TauLoad/Util.py

python test.py
python TauLoad/Loader.py
python TauLoad/Util.py
