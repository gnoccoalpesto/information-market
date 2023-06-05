'''
TODO single set of vars for both python and bash
https://stackoverflow.com/questions/17435056/read-bash-variables-into-a-python-script
'''
import os
import sys

# GLOBAL VARIABLES ##################################################################

# used directories
#NOTE -- ATTENTION: IF YOU MOVE THIS FILE, YOU MUST UPDATE THE FOLLOWING LINES
PROJECT_DIR="/".join(os.path.dirname(os.path.realpath(sys.argv[0])).split("/")[:-1])
CONFIG_DIR=f"{PROJECT_DIR}/config"
DATA_DIR=f"{PROJECT_DIR}/data"
PLOT_DIR=f"{PROJECT_DIR}/plots"

# runtime logging
CONFIG_ERRORS_DIR=f"{PROJECT_DIR}/src/config_errors"
ERRORS_LOG_FILE=f"{PROJECT_DIR}/src/error.log"
CONFIG_RUN_LOG:bool = True

# data logging
RECORD_DATA:bool = True

# transactions logging
LOG_COMPLETED_TRANSATIONS:bool = False
LOG_REJECTED_TRANSATIONS:bool = False

# bad configs pruning at runtime
PRUNE_FILENAMES= False
PRUNE_NOT_BEST= True
# DELETE_PRUNED=False

# experiment variations
NEWCOMER_PHASE:bool = False
NEWCOMER_PHASE_DURATION:int = 5000
NEWCOMER_AMOUNT:int = 5
NEWCOMER_TYPE='honest'


## EXCEPTIONS
LOG_EXCEPTIONS:bool = True
IFE_COUNT=0
