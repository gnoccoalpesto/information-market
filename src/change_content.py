#!/usr/bin/env python3
import os
import sys

from config import CONFIG_DIR

'''
changes the value of a specific field in the json file

NOTE HARDCODED! ADAPT THE LOOP TO THE DEPTH OF SUBFOLDER OF INTEREST
'''
scandir=f"{CONFIG_DIR}/{sys.argv[1]}"
subdirs=[s.path for s in os.scandir(scandir) if s.is_dir()]

count_changed=0
for ssd in subdirs:
    for f in [s.path for s in os.scandir(ssd) if s.is_file()]:
        if f.endswith(".json"):
        #chenge content with sed
            os.system(f"sed -e 's|fcerri|uga/ing/tesi|g' {f} > temp.json")
            os.system(f"mv temp.json {f}")