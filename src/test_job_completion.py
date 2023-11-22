import os
import sys

from config import *
from model.behavior import SUB_FOLDERS_DICT
'''
compares if the number of submitted jobs is equal
 to the number of completed ones

usage: python3 test_job_completion.py <EXPERIMENT_DIR>
'''

#TODO add parsing for arg -t: trust config file
TRUST_COMPLETED=True

def alphabetical_order(l:list):
    '''
    organies list of strings in alphabetical order
    '''
    try:
        fp='/'.join(l[0].split('/')[:-1])
    except IndexError:
        print(f"ERROR: {l} is empty");exit()
    l=[x.split('/')[-1] for x in l]
    return [os.path.join(fp,f) for f in sorted(l, key=lambda s: s.lower())]


def get_submitted_subdirs(subdirs):
    '''
    returns list of subdirs that have been submitted and
        list of subdirs that have not been submitted
    '''
    subdirs_names=[s.split('/')[-1] for s in subdirs]
    not_submitted_subdirs=[os.path.join(experiment_dir, btt) 
                           for btt in behaviors_to_test if btt not in subdirs_names]
    return subdirs,not_submitted_subdirs


def get_completed_filenames(file):
    '''
    get the completefilenames from the config_log.txt file
    '''
    with open(file, 'r') as f:
        lines = f.readlines()
        filenames=[l.split('/')[-1].strip().split('.json')[0] 
                    for l in lines if l.startswith("OUTPUT FILENAME:")]
    return list(filter(None,list(set(filenames))))
                

def get_submitted_filenames(file):
    '''
    get the submitted filenames from the config_log.txt file
    '''
    with open(file, 'r') as f:
        lines = f.readlines()
        filenames=[l.split('/')[-1].strip().split('.json')[0]
                    for l in lines if not l.startswith("OUTPUT FILENAME:")]
    return list(filter(None,list(set(filenames))))


def test_not_completed(logfile,trust_completed=True):
    '''
    compares the number of submitted files with the number of completed files

    prints the ration of completed files and the list of missing files

    :param logfile: path to config_log.txt file
    :param trust_completed: if True, check is performed using the files present in a reference directory
                            instead of the ones listed in the config_log.txt file

    :return result: True if all files have been completed, False otherwise
    '''
    submitted_filenames=get_submitted_filenames(logfile)

    if trust_completed:
        completed_filenames=get_completed_filenames(logfile)
    else:
        subdir=logfile.split('config_log.txt')[0]
        fetchdir=os.path.join(subdir,'items_collected')
        completed_filenames=[f.split('.csv')[0] for _,_,files in os.walk(fetchdir) for f in files]
    print(f" {len(completed_filenames)} / {len(submitted_filenames)}")

    if len(submitted_filenames)!=len(completed_filenames):
        print("\tMISSING:")
        completed_filenames=[cf.replace('.','') for cf in completed_filenames]
        [print(sf) for sf in alphabetical_order(submitted_filenames) if sf not in completed_filenames]
        return False
    return True


##############################################
'''
argv[1]: experiment dir; the program will scan all the subdirs and print the ones present

argv[2:]: behaviors to test; this will be used to prune the present subdirs.
            if the number of behaviors to test is greater than the number of present subdirs,
            the subdirs missing from the experiment dir will be printed and consired as not submitted
            else, all the subdirs present in the experiment dir will be used

#TODO for not completed exp: search for common params combos,
#    ie find if [f1,...]=[P11*...P1n, ..., Pm1*...Pmn]
'''
try:
    experiment_dir=os.path.join(DATA_DIR,sys.argv[1])
    print(f"\nEXPERIMENT DIR: {experiment_dir}")
except IndexError:
    print("usage: python3 test_job_completion.py <EXPERIMENT_DIR> [<BEHAVIOR_INITIAL_1> ... <B_I_n>]")
    exit()

experiment_behaviors=alphabetical_order([os.path.join(experiment_dir, s) for s in os.listdir(experiment_dir) 
                  if os.path.isdir(os.path.join(experiment_dir, s))])
print(f"present: {[eb.split('/')[-1] for eb in experiment_behaviors]}")

behaviors_to_test=list(filter(None,list(set([SUB_FOLDERS_DICT[b] for b in sys.argv[2:]]))))
if len(behaviors_to_test)>0:
    behaviors_to_test=alphabetical_order(behaviors_to_test)
    print(f"to test: {behaviors_to_test}")
    if len(behaviors_to_test)>len([eb.split('/')[-1] for eb in experiment_behaviors]):
        experiment_behaviors,not_submitted_subdirs=get_submitted_subdirs(experiment_behaviors)
        print('-'*50)
        print(f"to test present: {[eb.split('/')[-1] for eb in experiment_behaviors]}")
        print(f"not submitted: {[ns.split('/')[-1] for ns in not_submitted_subdirs]}")
        print('-'*50)
    else:
        experiment_behaviors=[os.path.join(experiment_dir, btt) for btt in behaviors_to_test]

result=True
print("\n--------\nCOMPLETED CONFIGURATIONS:\n")
for eb in experiment_behaviors:
    logfile=f"{eb}/config_log.txt"
    print(f"{eb.split('/')[-1]}:",end=" ")
    result=result*test_not_completed(logfile,trust_completed=TRUST_COMPLETED)
    print()
if result: print("-----\nALL COMPLETED <3")
else: print("-----\nNOT ALL COMPLETED :(")
    