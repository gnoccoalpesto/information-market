#!/bin/sh

## Resource Request
#SBATCH --job-name=info_market                      # for squeue
#SBATCH --output=/home/fcerri/log/out/im_%j.stdout  # output file, %j will be replaced by the Job ID
#SBATCH --error=/home/fcerri/log/err/im_%j.stderr   # error file
#SBATCH --partition=Xeon6138                        # the hardware that you want to run on
# also: Xeon6138, Epyc7452  
#SBATCH --qos=long                                  # queue (short, long)
# also: short
#SBATCH --ntasks=1                                  # launched by the job; set higher for MPI programs
#SBATCH --mem=1gb
#SBATCH --time=2:00:00                              # the time that you want to allocate to your job
#SBATCH --cpus-per-task=5                           # cores per task on the same machine; set higher for OpenMP programs

PROJECT_DIR=$1
shift
EXEC_FILE="${PROJECT_DIR}/src/info_market.py"

## Output folder


## Dependencies
source  ${ENV_DIR}/bin/activate


## Job
# possible output redirection
python3 ${EXEC_FILE} $1 #> /tmp/fcerri/my_program.stdout


## Deactivate env
deactivate
