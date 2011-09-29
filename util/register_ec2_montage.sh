for x in 00 01 02 03 04 05 06 07 08 09 10;do
    ./scripts/gmreg.py -i data2 -f nfs -w montage -n 128 -l ec2 \
        /mnt/proflog/ec2/montage_result/data2_128_$x/work.txt /mnt/proflog/ec2/montage_result/data2_128_$x/workparp.db
done

