#!/bin/sh

## Resource Request
#SBATCH --job-name=info_market                              # for squeue
#SBATCH --output=/home/fcerri/log/out/im_%j.stdout          # output file, %j will be replaced by the Job ID
#SBATCH --error=/home/fcerri/log/err/im_%j.stderr           # error file
#SBATCH --partition=XeonE52680                              # the hardware that you want to run on (Xeon6138, Epyc7452  ,XeonE52680, Opteron6272)
#SBATCH --qos=long                                          # queue (short, long)
#SBATCH --ntasks=1                                          # launched by the job; set higher for MPI programs
#SBATCH --mem=3gb                                           # memory per node
#SBATCH --time=20:00:00                                     # STRICT DEADLINE; time you want to allocate to the job
#SBATCH --cpus-per-task=5                                   # cores per task on the same machine; set higher for OpenMP programs

PROJECT_DIR=$1
shift
EXEC_FILE="${PROJECT_DIR}/src/info_market.py"


## Dependencies
source  ${ENV_DIR}/bin/activate


## Job      #NOTE       possible output redirection
python3 ${EXEC_FILE} $1 #> /tmp/fcerri/my_program.stdout


## Deactivate env
deactivate
