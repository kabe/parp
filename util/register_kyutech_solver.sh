#!/bin/sh

CWDIR=`dirname 0`

BINARY=$CWDIR/../tau/register_profgroup.py
#BINOPT="-v -b"

CMD="$BINARY $BINOPT"

# solver
SOLVER_BASE=/mnt/proflog/dmi_kabe/tmp/

# 128 nodes
MAP=solver_mpich2_tau_kyutech.map
PROFS="`seq 19919 19923` `seq 32305 32309`"
for x in $PROFS;do
    $CMD --place kyutech --library "MPICH2 GCC NFS" $SOLVER_BASE/mpich2-1.2.1_$x.kyutech-charlie.isc.kyutech.ac.jp $SOLVER_BASE/$MAP
done

MAP=solver_openmpi_tau_kyutech.map
PROFS="`seq 19924 19928` `seq 32310 32314`"
for x in $PROFS;do
    $CMD --place kyutech --library "OpenMPI GCC NFS" $SOLVER_BASE/openmpi_$x.kyutech-charlie.isc.kyutech.ac.jp $SOLVER_BASE/$MAP
done


