for x in 01 02 03 04 05 06 07 08 09 10;do
    ./scripts/gmreg.py -i data2 -f lustre -w jawc -n 128 -l tsubame2 \
        /mnt/proflog/tsubame2/jawc_result/data2_lustre_11-128_2_$x/work.txt /mnt/proflog/tsubame2/jawc_result/data2_lustre_11-128_2_$x/workparp.db
done
