#!/bin/sh

CWDIR=`dirname 0`

BINARY=$CWDIR/../tau/register_profgroup.py
APPNAME=FileAccess
#BINOPT="-v -b"

CMD="$BINARY $BINOPT"

# HA8000
BASE=/mnt/proflog/ha8000-fileaccess

MAP=file_access2.2.map
for x in hsfs lustre nfs;do
    $CMD --place ha8000 --library "MPICH2 MX GCC $x" --appname $APPNAME $BASE/708987.batch1_$x $BASE/$MAP
done

