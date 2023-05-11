import os
import sys

from config import *
from data_analysis import dataframe_from_csv

'''
compares if the number of submitted jobs is equal
 to the number of completed ones

usage: python3 test_job_completion.py <EXPERIMENT_DIR>
'''
scandir=f"{DATA_DIR}/{sys.argv[1]}"

subdirs=[f.path for f in os.scandir(scandir) if f.is_dir()]
FILE_COUNT=0
COUNT_OK=0
COUNT_0_5=0
COUNT_5_15=0
COUNT_15_50=0
COUNT_50_100=0
COUNT_100_150=0
max_ddiff=0
max_ddiff_name=""
NP_COUNT=0
P_COUNT=0
NRS_COUNT=0
RS_COUNT=0
for sd in subdirs:
    for f in os.scandir(sd+'/rewards'):
        if f.is_file():
            FILE_COUNT+=1
            SHOW=False
            df=dataframe_from_csv(f.path,post_processing="row-sum")
            for dd in df:
                ddiff=abs(dd-150)
                if ddiff>max_ddiff:
                    max_ddiff=ddiff
                    max_ddiff_name=f.path.split('/')[-1]
                if ddiff<=1e-3:
                    COUNT_OK+=1
                else:
                    SHOW=True
                    # print(f"dd: {dd}")

                    if "_NP_" in f.path.split('/')[-1]:
                        NP_COUNT+=1
                    elif "_P_" in f.path.split('/')[-1]:
                        P_COUNT+=1
                        if "_NRS_" in f.path.split('/')[-1]:
                            NRS_COUNT+=1
                        elif "_RS_" in f.path.split('/')[-1]:
                            RS_COUNT+=1

                    if ddiff<5:
                        COUNT_0_5+=1
                    elif ddiff<15:
                        COUNT_5_15+=1
                    elif ddiff<50:
                        COUNT_15_50+=1
                    elif ddiff<100:
                        COUNT_50_100+=1
                    else:
                        # print(f"dd: {dd}")
                        COUNT_100_150+=1
            if SHOW:
                print(f.path.split('/')[-1])
                [print(dd) for dd in df]

print(f"COUNT_OK: {COUNT_OK}")
print(f"COUNT_0_5: {COUNT_0_5}")
print(f"COUNT_5_15: {COUNT_5_15}")
print(f"COUNT_15_50: {COUNT_15_50}")
print(f"COUNT_50_100: {COUNT_50_100}")
print(f"COUNT_100_150: {COUNT_100_150}")
print(f"max_ddiff: {max_ddiff}")
print(f"max_ddiff_name: {max_ddiff_name}")
print(f"NP_COUNT: {NP_COUNT}")
print(f"P_COUNT: {P_COUNT}")
print(f"---NRS_COUNT: {NRS_COUNT}")
print(f"---RS_COUNT: {RS_COUNT}")
print(f"===FILE_COUNT: {FILE_COUNT}===")

              
#     scanfile=f"{sd}/config_log.txt"
#     count_submitted=0
#     count_completed=0
#     with open(scanfile, 'r') as f:
#         lines = f.readlines()
#         for l in lines:
#             if l.startswith("OUTPUT FILENAME:"):
#                 count_completed+=1
#             else:
#                 count_submitted+=1
#     if count_submitted!=count_completed:
#         result=False
#     print(f"{sd} -- submitted: {count_submitted} -- completed: {count_completed}")

# print(f"result: {'all completed' if result else 'not all completed'}")