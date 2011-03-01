#!/bin/sh

CWDIR=`dirname 0`

BINARY=$CWDIR/../tau/register_profgroup.py
#BINOPT="-v -b"

CMD="$BINARY $BINOPT"

# solver
SOLVER_BASE=/mnt/proflog/cloko-solver
# 128 nodes on 64 cores
MAP=solver_mpich2_tau.map
PROFS=`seq 979075 979084`
for x in $PROFS;do
    $CMD --place cloko --library "MPICH2 GCC NFS" $SOLVER_BASE/mpich2-1.2.1p1_${x}.clokofs-00.sc.iis.u-tokyo.ac.jp $SOLVER_BASE/$MAP
done

# 64 nodes
#MAP=solver_mpich2_tau.map
PROFS=`seq 979085 979094`
for x in $PROFS;do
    $CMD --place cloko --library "MPICH2 GCC NFS" $SOLVER_BASE/mpich2-1.2.1p1_${x}.clokofs-00.sc.iis.u-tokyo.ac.jp $SOLVER_BASE/$MAP
done

# 128 nodes
#MAP=solver_mpich2-mx-gcc-hsfs.map
PROFS=`seq 979065 979074`
for x in $PROFS;do
    $CMD --place cloko --library "MPICH2 GCC NFS" $SOLVER_BASE/mpich2-1.2.1p1_${x}.clokofs-00.sc.iis.u-tokyo.ac.jp $SOLVER_BASE/$MAP
done


