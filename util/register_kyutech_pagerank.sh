#!/bin/sh

CWDIR=`dirname 0`

BINARY=$CWDIR/../tau/register_profgroup.py
APPNAME=PageRank
#BINOPT="-v -b"

CMD="$BINARY $BINOPT"

# solver with trace
PR_BASE=/mnt/proflog/kyutech-pagerank

# 128 nodes w/ trace
MAP=pagerank_tau_mpich2.map
PROFS="`seq 32327 32336`"
for x in $PROFS;do
    $CMD --place kyutech --library "MPICH2 GCC NFS TRACE" --appname $APPNAME $PR_BASE/$x.kyutech-charlie.isc.kyutech.ac.jp $PR_BASE/$MAP
done

MAP=pagerank_tau_openmpi.map
PROFS="`seq 32339 32348`"
for x in $PROFS;do
    $CMD --place kyutech --library "OpenMPI GCC NFS TRACE" --appname $APPNAME $PR_BASE/$x.kyutech-charlie.isc.kyutech.ac.jp $PR_BASE/$MAP
done

# 128 nodes w/o trace
MAP=pagerank_tau_mpich2.map
PROFS="`seq 33013 33022`"
for x in $PROFS;do
    $CMD --place kyutech --library "MPICH2 GCC NFS" --appname $APPNAME $PR_BASE/$x.kyutech-charlie.isc.kyutech.ac.jp $PR_BASE/$MAP
done

MAP=pagerank_tau_openmpi.map
PROFS="`seq 33023 33032`"
for x in $PROFS;do
    $CMD --place kyutech --library "OpenMPI GCC NFS" --appname $APPNAME $PR_BASE/$x.kyutech-charlie.isc.kyutech.ac.jp $PR_BASE/$MAP
done


