for x in 01 02 03 04 05 06 07 08 09 10;do
    ./scripts/gmreg.py -i data2 -f nfs -w jawc -n 128 -l ec2 \
        /mnt/proflog/ec2/jawc_result/data2_128_2_$x/work.txt /mnt/proflog/ec2/jawc_result/data2_128_2_$x/workparp.db
done
