import os
import sys

from config import DATA_DIR

'''
usefull utility to adapt the names of the files in the dataset

usually start from data/FOLDER

NOTE HARDCODED! ADAPT THE LOOP TO THE DEPTH OF SUBFOLDER OF INTEREST
'''
scandir=f"{DATA_DIR}/{sys.argv[1]}"
print(f"scanning {scandir}")
subdirs=[s.path for s in os.scandir(scandir) if s.is_dir()]

count_changed=0
for ssd in subdirs:
    # for ssd in [s.path for s in os.scandir(sd) if s.is_dir()]:
        for f in [s.path for s in os.scandir(ssd) if s.is_file()]:
            if f.endswith(".csv"):
                dir,fo=f.split("/")[:-1], f.split("/")[-1]
                f=fo.replace("TM_", "TM_1SC_1KD_")
                os.rename(f"{'/'.join(dir)}/{fo}", f"{'/'.join(dir)}/{f}")
                count_changed+=1
print(f"changed {count_changed} files")