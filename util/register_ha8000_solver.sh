#!/bin/sh

CWDIR=`dirname 0`

BINARY=$CWDIR/../tau/register_profgroup.py
APPNAME=Solver
#BINOPT="-v -b"

CMD="$BINARY $BINOPT"

# HA8000 solver
HA8000_SOLVER_BASE=/mnt/proflog/ha8000-solver
# 64 nodes
MAP=solver_mpich2-mx-gcc-hsfs.map
PROFS=`seq 670963 670972`
for x in $PROFS;do
    $CMD --place ha8000 --library "MPICH2 MX GCC HSFS" --appname $APPNAME $HA8000_SOLVER_BASE/$x.batch1 $HA8000_SOLVER_BASE/$MAP
done

MAP=solver_mpich2-mx-gcc-nfs.map
PROFS=`seq 670974 670983`
for x in $PROFS;do
    $CMD --place ha8000 --library "MPICH2 MX GCC NFS" --appname $APPNAME $HA8000_SOLVER_BASE/$x.batch1 $HA8000_SOLVER_BASE/$MAP
done

MAP=solver_mpich2-mx-gcc-lustre.map
PROFS=`seq 671109 671118`
for x in $PROFS;do
    $CMD --place ha8000 --library "MPICH2 MX GCC LUSTRE" --appname $APPNAME $HA8000_SOLVER_BASE/$x.batch1 $HA8000_SOLVER_BASE/$MAP
done

MAP=solver_openmpi-mx-gcc-hsfs.map
PROFS="`seq 671190 671197` `seq 671199 671200`"
for x in $PROFS;do
    $CMD --place ha8000 --library "OPENMPI MX GCC HSFS" --appname $APPNAME $HA8000_SOLVER_BASE/$x.batch1 $HA8000_SOLVER_BASE/$MAP
done

MAP=solver_openmpi-mx-gcc-nfs.map
PROFS="`seq 671304 671310` `seq 671312 671314`"
for x in $PROFS;do
    $CMD --place ha8000 --library "OPENMPI MX GCC NFS" --appname $APPNAME $HA8000_SOLVER_BASE/$x.batch1 $HA8000_SOLVER_BASE/$MAP
done

MAP=solver_openmpi-mx-gcc-lustre.map
PROFS=`seq 671435 671444`
for x in $PROFS;do
    $CMD --place ha8000 --library "OPENMPI MX GCC LUSTRE" --appname $APPNAME $HA8000_SOLVER_BASE/$x.batch1 $HA8000_SOLVER_BASE/$MAP
done

# 128 nodes
MAP=solver_mpich2-mx-gcc-hsfs.map
PROFS="`seq 682644 682651` `seq 682680 682681`"
for x in $PROFS;do
    $CMD --place ha8000 --library "MPICH2 MX GCC HSFS" --appname $APPNAME $HA8000_SOLVER_BASE/$x.batch1 $HA8000_SOLVER_BASE/$MAP
done

MAP=solver_mpich2-mx-gcc-nfs.map
PROFS="`seq 682682 682687` `seq 682691 682694`"
for x in $PROFS;do
    $CMD --place ha8000 --library "MPICH2 MX GCC NFS" --appname $APPNAME $HA8000_SOLVER_BASE/$x.batch1 $HA8000_SOLVER_BASE/$MAP
done

MAP=solver_mpich2-mx-gcc-lustre.map
PROFS="`seq 682696 682699` `seq 682702 682707`"
for x in $PROFS;do
    $CMD --place ha8000 --library "MPICH2 MX GCC LUSTRE" --appname $APPNAME $HA8000_SOLVER_BASE/$x.batch1 $HA8000_SOLVER_BASE/$MAP
done

MAP=solver_openmpi-mx-gcc-hsfs.map
PROFS="`seq 682708 682709` `seq 682721 682728`"
for x in $PROFS;do
    $CMD --place ha8000 --library "OPENMPI MX GCC HSFS" --appname $APPNAME $HA8000_SOLVER_BASE/$x.batch1 $HA8000_SOLVER_BASE/$MAP
done

MAP=solver_openmpi-mx-gcc-nfs.map
PROFS="`seq 682853 682860` `seq 682864 682865`"
for x in $PROFS;do
    $CMD --place ha8000 --library "OPENMPI MX GCC NFS" --appname $APPNAME $HA8000_SOLVER_BASE/$x.batch1 $HA8000_SOLVER_BASE/$MAP
done

MAP=solver_openmpi-mx-gcc-lustre.map
PROFS="`seq 682866 682867` `seq 682874 682881`"
for x in $PROFS;do
    $CMD --place ha8000 --library "OPENMPI MX GCC LUSTRE" --appname $APPNAME $HA8000_SOLVER_BASE/$x.batch1 $HA8000_SOLVER_BASE/$MAP
done

