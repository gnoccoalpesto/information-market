#!/bin/sh

DIR="$1"

for file in "$DIR"/*.json; do
    sbatch /home/fcerri/information-market/cluster_job.sh $file
done