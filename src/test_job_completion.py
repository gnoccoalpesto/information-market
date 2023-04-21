import os
import sys

from config import *

'''
compares if the number of submitted jobs is equal
 to the number of completed ones

usage: python3 test_job_completion.py <EXPERIMENT_DIR>
'''
scandir=f"{DATA_DIR}/{sys.argv[1]}"

subdirs=[f.path for f in os.scandir(scandir) if f.is_dir()]

result=True

for sd in subdirs:
    scanfile=f"{sd}/config_log.txt"
    count_submitted=0
    count_completed=0
    with open(scanfile, 'r') as f:
        lines = f.readlines()
        for l in lines:
            if l.startswith("OUTPUT FILENAME:"):
                count_completed+=1
            else:
                count_submitted+=1
    if count_submitted!=count_completed:
        result=False
    print(f"{sd} -- submitted: {count_submitted} -- completed: {count_completed}")

print(f"result: {'all completed' if result else 'not all completed'}")