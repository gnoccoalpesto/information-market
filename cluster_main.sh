#!/bin/sh

DIR="$1"

for file in "$DIR"/*.json; do
    # echo "Processing $file"
    sbatch /home/uga/ing/tesi/information-market/cluster_job.sh $file
done