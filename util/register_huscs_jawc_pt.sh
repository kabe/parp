#!/bin/sh

PREFIX=/mnt/proflog/huscs-jawc-pt/jawc_pt_data2_128_2011-12-21_
for x in 01 02 03 04 05 06 07 08 09 10;do
    ./scripts/gmreg.py -i data2 -f nfs -w jawc-pt -n 128 -l huscs \
        -p "${PREFIX}$x/huscs*/trace.sqlite" -v \
        ${PREFIX}$x/work.txt ${PREFIX}$x/workparp.db
done

