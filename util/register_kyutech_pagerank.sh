#!/bin/sh

CWDIR=`dirname 0`

BINARY=$CWDIR/../tau/register_profgroup.py
#BINOPT="-v -b"

CMD="$BINARY $BINOPT"

# solver with trace
PR_BASE=/mnt/proflog/kyutech-pagerank

# 128 nodes
MAP=pagerank_tau_mpich2.map
PROFS="`seq 32327 32336`"
for x in $PROFS;do
    $CMD --place kyutech --library "MPICH2 GCC NFS TRACE" $PR_BASE/$x.kyutech-charlie.isc.kyutech.ac.jp $PR_BASE/$MAP
done

MAP=pagerank_tau_openmpi.map
PROFS="`seq 32339 32348`"
for x in $PROFS;do
    $CMD --place kyutech --library "OpenMPI GCC NFS TRACE" $PR_BASE/$x.kyutech-charlie.isc.kyutech.ac.jp $PR_BASE/$MAP
done


