#!/bin/sh

PREFIX=/home/kabe/proflog/tsubame2-jawc-pt/
for dir in gpfs lustre nfs; do
    echo Register $dir ...
    for x in `ls ${PREFIX}${dir}`;do
        ./scripts/gmreg.py -i data2 -f $dir -w jawc-pt -n 128 -l tsubame2 \
            -p "${PREFIX}${dir}/$x/*/trace.sqlite" -v \
            ${PREFIX}${dir}/$x/work.txt ${PREFIX}${dir}/$x/workparp.db
    done
    echo End Register $dir .

done
