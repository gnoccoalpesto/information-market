#!/bin/sh

## Resource Request
#SBATCH --job-name=info_market                      # for squeue
#SBATCH --output=/home/fcerri/log/out/im_%j.stdout  # output file, %j will be replaced by the Job ID
#SBATCH --error=/home/fcerri/log/err/im_%j.stderr   # error file
#SBATCH --partition=Epyc7452                        # the hardware that you want to run on
#SBATCH --qos=long                                  # queue (short, long)
#SBATCH --ntasks=1                                  # launched by the job; set higher for MPI programs
#SBATCH --mem=1gb
#SBATCH --time=2:00:00                              # the time that you want to allocate to your job
#SBATCH --cpus-per-task=20                           # cores per task on the same machine; set higher for OpenMP programs

## Dependencies
source  /home/fcerri/envs/tesi/bin/activate
# do i need to load modules once in the env?

## Job
python3 /home/fcerri/information-market/src/info_market.py $1

## Deactivate env
deactivate