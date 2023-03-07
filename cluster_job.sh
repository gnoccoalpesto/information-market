#!/bin/sh

## Resource Request
#SBATCH --job-name=test                             # for squeue
#SBATCH --output=/tmp/fcerri/test_%j.stdout         # output file, %j will be replaced by the Job ID
#SBATCH --error=/tmp/fcerri/test_%j.stderr          # error file
#SBATCH --partition=Epyc7452                        # the hardware that you want to run on
#SBATCH --qos=short                                 # queue (short, long)
#SBATCH --ntasks=1                                  # launched by the job; set higher for MPI programs
#SBATCH --mem=1gb
#SBATCH --time=5-22:00:00                           # the time that you want to allocate to your job
#SBATCH --cpus-per-task=1                           # cores per task on the same machine; set higher for OpenMP programs
#SBATCH --mail-user=francesco.cerri2@studio.unibo.it
#SBATCH --mail-type=END,FAIL                        # email notification; BEGIN, END, FAIL, ARRAY_TASKS


## Dependencies
source  /home/fcerri/envs/tesi/bin/activate
# do i need to load modules once in the env?


## Job
python3 /home/fcerri/information-market/src/info_market.py $1
