#!/bin/sh

####################################
# EXPECTED INPUT (at leat 2)
# 1 - FOLDER NAME TO CREATE IN TEMP
# 2: - CONFIG FILES, could be any combination of files and folders
####################################

usage(){
    echo "Usage: $0 <folder name for /tmp/`whoami`> <config files>"
    echo "Config files can be a combination of files and folders"
}

## INPUT CHECK
if [ $# -lt 2 ]; then
    usage
    exit 1
fi

## CREATE OUTPUT FOLDER
# tmp folder still not working
# MY_TEMP_FOLDER=/tmp/fcerri
MYDATA_FOLDER=$HOME/data
MY_NEW_FOLDER=$1
# mkdir -p $MY_TEMP_FOLDER/$MY_NEW_FOLDER
mkdir -p $MYDATA_FOLDER/$MY_NEW_FOLDER
shift 

## INPUT 
CONFIGS=""
for arg in $@; do
    if [ -d $arg ]; then
        toadd=$(find $arg -name "*.json")
    else # if-else construct is superior to elif
        if [ -f $1 ]; then
            toadd=$arg
        else
            echo "Invalid input"
            exit 1
        fi
    fi
    #newline not working, in bash could use \n or IFS ($IFS)
    CONFIGS="$CONFIGS $toadd"
done

## RUN
for file in $CONFIGS; do
    sbatch /home/fcerri/information-market/cluster_job.sh $file
    # should i use srun?
done

## TRANSFER DATA
    # mv $MY_TEMP_FOLDER/* $HOME/data/
# compress results first if you have many or very large files
    # should i use rsync?