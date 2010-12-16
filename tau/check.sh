#!/bin/sh

pep8 test.py
pep8 diff_top3.py
pep8 TauLoad/Loader.py
pep8 TauLoad/Util.py
pep8 nm/loader.py
pep8 register_profgroup.py

python test.py testcase/profile.0.0.0 testcase/solver_mpi_tau_pdt.map
python TauLoad/Loader.py
python TauLoad/Util.py
#python register_profgroup.py

pep8 db/__init__.py
pep8 db/kp_sqlite3.py
pep8 db/kp_postgres.py
python db/__init__.py
python db/kp_postgres.py
python db/kp_sqlite3.py
