#!/bin/sh

CWDIR=`dirname 0`

BINARY=$CWDIR/../tau/register_profgroup.py
APPNAME=FileAccess
#BINOPT="-v -b"

CMD="$BINARY $BINOPT"

# HA8000 solver
HA8000_SOLVER_BASE=/mnt/proflog/ha8000-fileaccess

MAP=file_access2.map
for x in hsfs lustre nfs;do
    $CMD --place ha8000 --library "MPICH2 MX GCC $x" --appname $APPNAME $HA8000_SOLVER_BASE/707763.batch1_$x $HA8000_SOLVER_BASE/$MAP
done

