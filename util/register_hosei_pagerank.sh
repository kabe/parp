#!/bin/sh

CWDIR=`dirname 0`

BINARY=$CWDIR/../tau/register_profgroup.py
APPNAME=PageRank
#BINOPT="-v -b"

CMD="$BINARY $BINOPT"

# solver with trace
PR_BASE=/mnt/proflog/hosei-pagerank

# 128 nodes w/ trace
MAP=pagerank_tau_mpich2.map
PROFS="`seq 15637 15646`"
for x in $PROFS;do
    $CMD --place hosei --library "MPICH2 GCC NFS" --appname $APPNAME $PR_BASE/$x.hosei-charlie.intrigger.cis.k.hosei.ac.jp $PR_BASE/$MAP
done

MAP=pagerank_tau_openmpi.map
PROFS="`seq 15648 15657`"
for x in $PROFS;do
    $CMD --place hosei --library "OpenMPI GCC NFS" --appname $APPNAME $PR_BASE/$x.hosei-charlie.intrigger.cis.k.hosei.ac.jp $PR_BASE/$MAP
done

MAP=pagerank_tau_openmpi.map
PROFS="`seq 22366 22375`"
for x in $PROFS;do
    $CMD --place hosei --library "OpenMPI-t GCC NFS" --appname $APPNAME $PR_BASE/$x.hosei-charlie.intrigger.cis.k.hosei.ac.jp $PR_BASE/$MAP
done


