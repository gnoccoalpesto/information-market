#!/bin/sh

####################################
# EXPECTED INPUT (at leat 2)
# 1 - FOLDER NAME TO CREATE IN TEMP
# 2: - CONFIG FILES, could be any combination of files and folders
####################################

PROJECT_HOME=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/..
CONFIG_DIR="${PROJECT_HOME}/config"
JOB_FILE="${PROJECT_HOME}/src/job_cluster.sh"


declare -A SUB_DIR_BEHAVIOR
	SUB_DIR_BEHAVIOR[n]="naive"
	SUB_DIR_BEHAVIOR[Nn]="new_naive"
	SUB_DIR_BEHAVIOR[s]="sceptical"
	SUB_DIR_BEHAVIOR[Ns]="new_sceptical"
	SUB_DIR_BEHAVIOR[r]="ranking"
	SUB_DIR_BEHAVIOR[v]="variable_scepticism"
	SUB_DIR_BEHAVIOR[Nv]="variable_scepticism"
	SUB_DIR_BEHAVIOR[t]="wealth_threshold"
	SUB_DIR_BEHAVIOR[w]="wealth_weighted"
    SUB_DIR_BEHAVIOR[h]="history"
    SUB_DIR_BEHAVIOR[hs]="history_sceptical"


usage(){
    # echo "Usage: $0 <folder name for /tmp/`whoami`> <config files>"
    echo "Usage: $0 <config files>"
    echo "Config files can be a combination of files and folders"
}


## INPUT CHECK
# if [ $# -lt 2 ]; then
if [ $# -lt 1 ]; then
    usage
    exit 1
fi


## CREATE OUTPUT FOLDER
#TODO
# MY_TEMP_DIR=/tmp/fcerri


## INPUT 
CONFIGS=""
for arg in $@; do
    #read all files from a dir
    if [ -d $arg ]; then
        c=$(find $arg -name "*.json")
    else # if-else construct is superior to elif
        #checks if it is file
        if [ -f $arg ]; then
            c=$arg
        else
            #checks if a particular keyword for behavior (sub-folder)
            if [[ -v SUB_DIR_BEHAVIOR[$arg] ]]; then
                c=$(find $CONFIG_DIR/${SUB_DIR_BEHAVIOR[$arg]} -name "*.json")
            else
                echo "Invalid input"
                exit 1
            fi
        fi
    fi
    #newline not working, in bash could use \n or IFS ($IFS)
    CONFIGS="$CONFIGS $c"
done


## RUN
for file in $CONFIGS; do
    sbatch ${JOB_FILE} $file
done


## TRANSFER DATA
#TODO
    # mv $MY_TEMP_DIR/* $DATA_DIR
# compress results first if you have many or very large files
    # should i use rsync?