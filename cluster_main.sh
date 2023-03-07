#!/bin/sh

DIR="/home/fcerri/information-market/config/test/"
for file in "$DIR"/*.json; do
# do i need "$X" or $X?
    sbatch /home/uga/ing/tesi/information-market/cluster_job.sh $file
done