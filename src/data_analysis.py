import re
import os
from os.path import join
import argparse
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick # to plot percentage on axis for matplotlib
from  matplotlib.ticker import FuncFormatter #to force axis to have integer ticks
import seaborn as sns

import config as CONFIG_FILE
from model.environment import generate_uniform_noise_list
from model.behavior import  BEHAVIORS_NAME_DICT, SUB_FOLDERS_DICT, PARAMS_NAME_DICT, BEHAVIOR_PARAMS_DICT,COMBINE_STRATEGY_NAME_DICT
from info_market import filename_from_params, params_from_filename,is_bad_param_combination, is_best_param_combination


#  blue        orange    green     red        purple      brown     pink         grey      yellow    cyan
#'#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
#DEEP
#['#4c72b0', '#dd8452', '#55a868', '#c44e52', '#8172b3', '#937860', '#da8bc3', '#8c8c8c', '#ccb974', '#64b5cd']
#DARK
# ['#001c7f', '#b1400d', '#12711c', '#8c0800', '#591e71', '#592f0d', '#a23582', '#3c3c3c', '#b8850a', '#006374']
#PASTEL
#['#a1c9f4', '#ffb482', '#8de5a1', '#ff9f9b', '#d0bbff', '#debb9b', '#fab0e4', '#cfcfcf', '#fffea3', '#b9f2f0']
#COLORBLIND
#['#0173b2', '#de8f05', '#029e73', '#d55e00', '#cc78bc', '#ca9161', '#fbafe4', '#949494', '#ece133', '#56b4e9']
#BRIGHT
#['#023eff', '#ff7c00', '#1ac938', '#e8000b', '#8b2be2', '#9f4800', '#f14cc1', '#a3a3a3', '#ffc400', '#00d7ff']


BEHAVIOUR_PALETTE={'n':"#e377c2",#7, pink
                    'Naive':"#e377c2",
                    'Saboteur Naive':"#d62728",#4, red
                    'Nn':"#e377c2",
                    's':"#1f77b4",#1, blue
                    'Sceptical':"#1f77b4",
                    'Saboteur Sceptical':"#d62728",
                    'Ns':"#1f77b4",
                    'r':"#2ca02c",#3, green
                    'Rep. Ranking':"#2ca02c",
                    'Reputation Ranking':"#2ca02c",
                    'Saboteur Rep. Ranking':"#d62728",
                    'Saboteur Reputation Ranking':"#d62728",
                    'v':"#17becf",#10, cyan
                    'Nv':"#17becf",
                    'Variable Sc.':"#17becf",
                    'Variable Scepticism':"#17becf",
                    'Saboteur Variable Sc.':"#d62728",
                    'Saboteur Variable Scepticism':"#d62728",
                    't':"#ff7f0e",#2, orange
                    'Rep. Threshold':"#ff7f0e",
                    'Reputation Threshold':"#ff7f0e",
                    'Saboteur Rep. Threshold':"#d62728",
                    'Saboteur Reputation Threshold':"#d62728",
                    'h':"#9467bd",#5, purple
                    'Rep. History':"#9467bd",
                    'Reputation History':"#9467bd",
                    'Saboteur Rep. History':"#d62728",
                    'Saboteur Reputation History':"#d62728",
                    ###############QUALITY INDEXES############
                    #1
                    'Q1n':"#da8bc3",#7, pink deep
                    'Q1Naive':"#da8bc3",
                    'Q1s':"#4c72b0",#1, blue deep
                    'Q1Sceptical':"#4c72b0",
                    'Q1r':"#55a868",#3, green deep
                    'Q1Rep. Ranking':"#55a868",
                    'Q1Reputation Ranking':"#55a868",
                    'Q1Nv':"#17becf",#10, cyan deep
                    'Q1Variable Sc.':"#17becf",
                    'Q1Variable Scepticism':"#17becf",
                    'Q1t':"#dd8452",#2, orange deep
                    'Q1Rep. Threshold':"#dd8452",
                    'Q1Reputation Threshold':"#dd8452",
                    'Q1h':"#8172b3",#5, purple deep
                    'Q1Rep. History':"#8172b3",
                    'Q1Reputation History':"#8172b3",
                    #2
                    'Q2n':"#a23582",#7, pink dark
                    'Q2Naive':"#a23582",
                    'Q2s':"#001c7f",#1, blue dark
                    'Q2Sceptical':"#001c7f",
                    'Q2r':"#12711c",#3, green dark
                    'Q2Rep. Ranking':"#12711c",
                    'Q2Reputation Ranking':"#12711c",
                    'Q2Nv':"#006374",#10, cyan dark
                    'Q2Variable Sc.':"#006374",
                    'Q2Variable Scepticism':"#006374",
                    'Q2t':"#b1400d",#2, orange dark
                    'Q2Rep. Threshold':"#b1400d",
                    'Q2Reputation Threshold':"#b1400d",
                    'Q2h':"#591e71",#5, purple dark
                    'Q2Rep. History':"#591e71",
                    'Q2Reputation History':"#591e71",
                    #3
                    'Q3n':"#f14cc1",#7, pink bright
                    'Q3Naive':"#f14cc1",
                    'Q3s':"#023eff",#1, blue bright
                    'Q3Sceptical':"#023eff",
                    'Q3r':"#1ac938",#3, green bright
                    'Q3Rep. Ranking':"#1ac938",
                    'Q3Reputation Ranking':"#1ac938",
                    'Q3Nv':"#00d7ff",#10, cyan bright
                    'Q3Variable Sc.':"#00d7ff",
                    'Q3Variable Scepticism':"#00d7ff",
                    'Q3t':"#ff7c00",#2, orange bright
                    'Q3Rep. Threshold':"#ff7c00",
                    'Q3Reputation Threshold':"#ff7c00",
                    'Q3h':"#8b2be2",#5, purple bright
                    'Q3Rep. History':"#8b2be2",
                    'Q3Reputation History':"#8b2be2",
                    #4
                    'Q4n':"#fab0e4",#7, pink pastel
                    'Q4Naive':"#fab0e4",
                    'Q4s':"#a1c9f4",#1, blue pastel
                    'Q4Sceptical':"#a1c9f4",
                    'Q4r':"#8de5a1",#3, green pastel
                    'Q4Rep. Ranking':"#8de5a1",
                    'Q4Reputation Ranking':"#8de5a1",
                    'Q4Nv':"#b9f2f0",#10, cyan pastel
                    'Q4Variable Sc.':"#b9f2f0",
                    'Q4Variable Scepticism':"#b9f2f0",
                    'Q4t':"#ffb482",#2, orange pastel
                    'Q4Rep. Threshold':"#ffb482",
                    'Q4Reputation Threshold':"#ffb482",
                    'Q4h':"#d0bbff",#5, purple pastel
                    'Q4Rep. History':"#d0bbff",
                    'Q4Reputation History':"#d0bbff",
                    #5
                    'Q5n':"#fbafe4",#7, pink colorblind
                    'Q5Naive':"#fbafe4",
                    'Q5s':"#0173b2",#1, blue colorblind
                    'Q5Sceptical':"#0173b2",
                    'Q5r':"#029e73",#3, green colorblind
                    'Q5Rep. Ranking':"#029e73",
                    'Q5Reputation Ranking':"#029e73",
                    'Q5Nv':"#17becf",#10, cyan colorblind
                    'Q5Variable Sc.':"#17becf",
                    'Q5Variable Scepticism':"#17becf",
                    'Q5t':"#de8f05",#2, orange colorblind
                    'Q5Rep. Threshold':"#de8f05",
                    'Q5Reputation Threshold':"#de8f05",
                    'Q5h':"#cc78bc",#5, purple colorblind
                    'Q5Rep. History':"#cc78bc",
                    'Q5Reputation History':"#cc78bc",
                    #dishonests: 
                    'QDn':"#e8000b",# bright red
                    'QDNaive':"#e8000b",
                    'QDs':"#e8000b",
                    'QDSceptical':"#e8000b",
                    'QDr':"#e8000b",
                    'QDRep. Ranking':"#e8000b",
                    'QDReputation Ranking':"#e8000b",
                    'QDNv':"#e8000b",
                    'QDVariable Sc.':"#e8000b",
                    'QDVariable Scepticism':"#e8000b",
                    'QDt':"#e8000b",
                    'QDRep. Threshold':"#e8000b",
                    'QDReputation Threshold':"#e8000b",
                    'QDh':"#e8000b",
                    'QDRep. History':"#e8000b",
                    'QDReputation History':"#e8000b",
                    'NEWn':"#a3a3a3",# grey
                    'NEWNaive':"#a3a3a3",
                    'NEWs':"#a3a3a3",
                    'NEWSceptical':"#a3a3a3",
                    'NEWr':"#a3a3a3",
                    'NEWRep. Ranking':"#a3a3a3",
                    'NEWReputation Ranking':"#a3a3a3",
                    'NEWNv':"#a3a3a3",
                    'NEWVariable Sc.':"#a3a3a3",
                    'NEWVariable Scepticism':"#a3a3a3",
                    'NEWt':"#a3a3a3",
                    'NEWRep. Threshold':"#a3a3a3",
                    'NEWReputation Threshold':"#a3a3a3",
                    'NEWh':"#a3a3a3",
                    'NEWRep. History':"#a3a3a3",
                    'NEWReputation History':"#a3a3a3",
                    }
BEHAV_PARAMS_COMBINATIONS={"n":[[]],
                                "s":[[0.25]],
                                "r":[
                                    # [0.3],
                                    [0.5]
                                    ],
                                "Nv":[
                                    # ["allavg",0.3,0.25,"exponential"],
                                    # ["allavg",0.5,0.25,"exponential"],
                                    # ["allavg",0.8,0.25,"exponential"],
                                    ["allavg",0.3,0.25,"ratio"],
                                    ["allavg",0.5,0.25,"ratio"],
                                    # ["allavg",0.8,0.25,"ratio"],
                                    # ["allmax",0.3,0.25,"exponential"],
                                    # ["allmax",0.5,0.25,"exponential"],
                                    # ["allmax",0.8,0.25,"exponential"],
                                    # ["allmax",0.3,0.25,"ratio"],
                                    # ["allmax",0.5,0.25,"ratio"],
                                    # ["allmax",0.8,0.25,"ratio"]
                                    ],
                                "t":[
                                    # ["allavg",0.3],
                                    ["allavg",0.5],
                                    # ["allavg",0.8],
                                    # ["allmax",0.3],
                                    # ["allmax",0.5],
                                    # ["allmax",0.8]
                                    ],
                                "w":[[]],
                                "h":[
                                    ["aged","mean",0.8,1],#------------------------------
                                    # ["aged2","mean",0.8,1.3],#----------------------------
                                    ["discrete","mean",1,1],#-------------------------------
                                    # ["discrete","positive",1,1],#################
                                    ["difference","mean",1,1],########################
                                    # ["difference","positive",1,1],#####################
                                    # ["recency","mean",1,1],###############
                                    # ["recency","positive",1,1],###############
                                    ["aged","mean",1,1],################
                                    # ["aged","positive",1,1],################
                                    # ["aged2","mean",1,1],######################
                                    # ["aged2","positive",1,1],######################
                                    # ["discrete","mean",0.3,0.7],
                                    # ["discrete","positive",0.3,0.7],
                                    # ["discrete","mean",0.5,0.7],
                                    # ["discrete","mean",0.8,0.7],
                                    # ["discrete","positive",0.5,0.7],
                                    # ["discrete","positive",0.8,0.7],
                                    # ["discrete","mean",1,0.7],
                                    # ["discrete","positive",1,0.7],
                                    # ["discrete","mean",0.3,1],
                                    # ["discrete","positive",0.3,1],
                                    # ["discrete","mean",0.5,1],
                                    # ["discrete","positive",0.5,1],
                                    # ["discrete","mean",0.8,1],
                                    # ["discrete","positive",0.8,1],
                                    # ["discrete","mean",0.3,1.3],
                                    # ["discrete","positive",0.3,1.3],
                                    # ["discrete","mean",0.5,1.3],
                                    # ["discrete","positive",0.5,1.3],
                                    # ["discrete","mean",0.8,1.3],
                                    # ["discrete","positive",0.8,1.3],
                                    # ["discrete","mean",1,1.3],
                                    # ["discrete","positive",1,1.3],
                                    # ["discrete","mean",0.3,1.6],
                                    # ["discrete","positive",0.3,1.6],
                                    # ["discrete","mean",0.5,1.6],
                                    # ["discrete","positive",0.5,1.6],
                                    # ["discrete","mean",0.8,1.6],
                                    # ["discrete","positive",0.8,1.6],
                                    # ["discrete","mean",1,1.6],
                                    # ["discrete","positive",1,1.6],
                                    # ["discrete","mean",0.3,2.0],
                                    # ["discrete","positive",0.3,2.0],
                                    # ["discrete","mean",0.5,2.0],
                                    # ["discrete","positive",0.5,2.0],
                                    # ["discrete","mean",0.8,2.0],
                                    # ["discrete","positive",0.8,2.0],
                                    # ["discrete","mean",1,2.0],
                                    # ["discrete","positive",1,2.0],
                                    # ["difference","mean",0.3,0.7],
                                    # ["difference","positive",0.3,0.7],
                                    # ["difference","mean",0.5,0.7],
                                    # ["difference","positive",0.5,0.7],
                                    # ["difference","mean",0.8,0.7],
                                    # ["difference","positive",0.8,0.7],
                                    # ["difference","mean",1,0.7],
                                    # ["difference","positive",1,0.7],
                                    # ["difference","mean",0.3,1],
                                    # ["difference","positive",0.3,1],
                                    # ["difference","mean",0.5,1],
                                    # ["difference","positive",0.5,1],
                                    # ["difference","mean",0.8,1],
                                    # ["difference","positive",0.8,1],
                                    # ["difference","mean",0.3,1.3],
                                    # ["difference","positive",0.3,1.3],
                                    # ["difference","mean",0.5,1.3],
                                    # ["difference","positive",0.5,1.3],
                                    # ["difference","mean",0.8,1.3],
                                    # ["difference","positive",0.8,1.3],
                                    # ["difference","mean",1,1.3],
                                    # ["difference","positive",1,1.3],
                                    # ["difference","mean",0.3,1.6],
                                    # ["difference","positive",0.3,1.6],
                                    # ["difference","mean",0.5,1.6],
                                    # ["difference","positive",0.5,1.6],
                                    # ["difference","mean",0.8,1.6],
                                    # ["difference","positive",0.8,1.6],
                                    # ["difference","mean",1,1.6],
                                    # ["difference","positive",1,1.6],
                                    # ["difference","mean",0.3,2.0],
                                    # ["difference","positive",0.3,2.0],
                                    # ["difference","mean",0.5,2.0],
                                    # ["difference","positive",0.5,2.0],
                                    # ["difference","mean",0.8,2.0],
                                    # ["difference","positive",0.8,2.0],
                                    # ["difference","mean",1,2.0],
                                    # ["difference","positive",1,2.0],
                                    # ["recency","mean",0.3,0.7],
                                    # ["recency","positive",0.3,0.7],
                                    # ["recency","mean",0.5,0.7],
                                    # ["recency","positive",0.5,0.7],
                                    # ["recency","mean",0.8,0.7],
                                    # ["recency","positive",0.8,0.7],
                                    # ["recency","mean",1,0.7],
                                    # ["recency","positive",1,0.7],
                                    # ["recency","mean",0.3,1],
                                    # ["recency","positive",0.3,1],
                                    # ["recency","mean",0.5,1],
                                    # ["recency","positive",0.5,1],
                                    # ["recency","mean",0.8,1],
                                    # ["recency","positive",0.8,1],
                                    # ["recency","mean",0.3,1.3],
                                    # ["recency","positive",0.3,1.3],
                                    # ["recency","mean",0.5,1.3],
                                    # ["recency","positive",0.5,1.3],
                                    # ["recency","mean",0.8,1.3],
                                    # ["recency","positive",0.8,1.3],
                                    # ["recency","mean",1,1.3],
                                    # ["recency","positive",1,1.3],
                                    # ["recency","mean",0.3,1.6],
                                    # ["recency","positive",0.3,1.6],
                                    # ["recency","mean",0.5,1.6],
                                    # ["recency","positive",0.5,1.6],
                                    # ["recency","mean",0.8,1.6],
                                    # ["recency","positive",0.8,1.6],
                                    # ["recency","mean",1,1.6],
                                    # ["recency","positive",1,1.6],
                                    # ["recency","mean",0.3,2.0],
                                    # ["recency","positive",0.3,2.0],
                                    # ["recency","mean",0.5,2.0],
                                    # ["recency","positive",0.5,2.0],
                                    # ["recency","mean",0.8,2.0],
                                    # ["recency","positive",0.8,2.0],
                                    # ["recency","mean",1,2.0],
                                    # ["recency","positive",1,2.0],
                                    # ["aged","mean",0.3,0.7],
                                    # ["aged","positive",0.3,0.7],
                                    # ["aged","mean",0.5,0.7],
                                    # ["aged","positive",0.5,0.7],
                                    # ["aged","mean",0.8,0.7],
                                    # ["aged","positive",0.8,0.7],
                                    # ["aged","mean",1,0.7],
                                    # ["aged","positive",1,0.7],
                                    # ["aged","mean",0.3,1],
                                    # ["aged","positive",0.3,1],
                                    # ["aged","mean",0.5,1],
                                    # ["aged","positive",0.5,1],
                                    # ["aged","positive",0.8,1],
                                    # ["aged","mean",0.3,1.3],
                                    # ["aged","positive",0.3,1.3],
                                    # ["aged","mean",0.5,1.3],
                                    # ["aged","positive",0.5,1.3],
                                    # ["aged","mean",0.8,1.3],
                                    # ["aged","positive",0.8,1.3],
                                    # ["aged","mean",1,1.3],
                                    # ["aged","positive",1,1.3],
                                    # ["aged","mean",0.3,1.6],
                                    # ["aged","positive",0.3,1.6],
                                    # ["aged","mean",0.5,1.6],
                                    # ["aged","positive",0.5,1.6],
                                    # ["aged","mean",0.8,1.6],
                                    # ["aged","positive",0.8,1.6],
                                    # ["aged","mean",1,1.6],
                                    # ["aged","positive",1,1.6],
                                    # ["aged","mean",0.3,2.0],
                                    # ["aged","positive",0.3,2.0],
                                    # ["aged","mean",0.5,2.0],
                                    # ["aged","positive",0.5,2.0],
                                    # ["aged","mean",0.8,2.0],
                                    # ["aged","positive",0.8,2.0],
                                    # ["aged","mean",1,2.0],
                                    # ["aged","positive",1,2.0],
                                    # ["aged2","mean",0.3,0.7],
                                    # ["aged2","positive",0.3,0.7],
                                    # ["aged2","mean",0.5,0.7],
                                    # ["aged2","positive",0.5,0.7],
                                    # ["aged2","mean",0.8,0.7],
                                    # ["aged2","positive",0.8,0.7],
                                    # ["aged2","mean",1,0.7],
                                    # ["aged2","positive",1,0.7],
                                    # ["aged2","mean",0.3,1],
                                    # ["aged2","positive",0.3,1],
                                    # ["aged2","mean",0.5,1],
                                    # ["aged2","positive",0.5,1],
                                    # ["aged2","mean",0.8,1],
                                    # ["aged2","positive",0.8,1],
                                    # ["aged2","mean",0.3,1.3],
                                    # ["aged2","positive",0.3,1.3],
                                    # ["aged2","mean",0.5,1.3],
                                    # ["aged2","positive",0.5,1.3],
                                    # ["aged2","positive",0.8,1.3],
                                    # ["aged2","mean",1,1.3],
                                    # ["aged2","positive",1,1.3],
                                    # ["aged2","mean",0.3,1.6],
                                    # ["aged2","positive",0.3,1.6],
                                    # ["aged2","mean",0.5,1.6],
                                    # ["aged2","positive",0.5,1.6],
                                    # ["aged2","mean",0.8,1.6],
                                    # ["aged2","positive",0.8,1.6],
                                    # ["aged2","mean",1,1.6],
                                    # ["aged2","positive",1,1.6],
                                    # ["aged2","mean",0.3,2.0],
                                    # ["aged2","positive",0.3,2.0],
                                    # ["aged2","mean",0.5,2.0],
                                    # ["aged2","positive",0.5,2.0],
                                    # ["aged2","mean",0.8,2.0],
                                    # ["aged2","positive",0.8,2.0],
                                    # ["aged2","mean",1,2.0],
                                    # ["aged2","positive",1,2.0],
                                    ],
                                }



############################################################################################################
############################################################################################################
################################## UTILITIES ###############################################################
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--standalone',action='store_true',
                    help='considers metric for single robot')
    parser.add_argument('-p', '--relative','--percent',action='store_true',
                    help='considers metric relative to total of experiment')
    parser.add_argument('-c', '--comulative',action='store_true',
                    help='consider comulated metric for an experiment')
    parser.add_argument('-i','--items-collected', action='store_true',
                        help='consider as metric the number of items collected')
    parser.add_argument('-r', '--rewards', action='store_true',
                        help='consider as metric rewards')
    args=parser.parse_args()
    if args.items_collected:
        metric="items_collected"
    elif args.rewards:
        metric="rewards"
    else:
        print("Automatically selected metric: items_collected")
        metric="items_collected"
    if args.standalone:
        mode="s"
    elif args.relative:
        mode="r"
    elif args.comulative:
        mode="c"
    else:
        print("Automatically selected mode: c (comulative)")
        mode="c"
    return metric, mode


def dataframe_from_csv(filename,
                        data_folder_and_subfolder="",
                        metric="",
                        experiment_part="whole",
                        noise_group="all",
                        post_processing=None,
                    ):
    '''
    returns the appropriate DataFrame, given the filename and the experiment part

    :param filename: the name of the file to load, must include the extension

    :UNUSED param data_folder_and_subfolder: the folder where the data is stored, must include up to the metric

    :UNUSED param metric: the metric to choose from.  Accepted values are:
        "items": number of items collected by the robots;
        "rewards": rewards gained by the robots;
        "transaction(s)Q": number of transactions made by the robots. Q is a parameter indicating
            the type of transaction to consider. Accepted values are:
            - "A": attempted transactions;
            - "V": validated transactions;
            - "C": completed transactions;
            - "X": combined transactions.

    :param experiment_part: the part of the experiment to load. Accepted values are:
         "whole": in this case the data from the end of the experiment is loaded;
            selected metric folders will be "items_collected" or "rewards"
         "lastN": in this case only the last N% of the experiment is considered;
            selected metric folders will be "items_evolution" or "rewards_evolution".
            Params ofr the loading will differe according to the different file format.

    :param post_processing: applies a function to the loaded data.
        Param has this format "ITEMS-FUNCTION". Accepted values are:
        {ITEMS]: "row", "exp", "experiment" : statistic relevant experiment-wise;
                 "col", "rob", "robot": statistic relevant robot-wise.
            Resulting DataFrame will have the shape the shape (n_rows, 1) or (1, n_cols), where
            n_rows==n_runs_experiment, n_cols==n_robots_experiment,

        {FUNCTION}: "sum", "mean", "std", "median", "min", "max"

    :return: the DataFrame containing the desidered data
    '''
    if not filename.endswith(".csv"): filename+=".csv"

    #NOTE as for now, only items are allowed to use lastN, for they monotonic
    #   non decreasing nature

    if experiment_part=="whole" or "transaction" in metric \
        or 'reward' in filename:#NOTE BYPASS NEGATIVE REWARD ISSUE
        # if metric=="items": metric_folder="items_collected"
        # elif "transaction" in metric:
        #     metric_folder="transactions"
        #     if "A" in metric: filename=filename.split(".csv")[0]+"_attempted.csv"
        #     elif "V" in metric: filename=filename.split(".csv")[0]+"_validated.csv"
        #     elif "C" in metric: filename=filename.split(".csv")[0]+"_completed.csv"
        #     elif "X" in metric: filename=filename.split(".csv")[0]+"_combined.csv"

        #     if "S" in metric: filename=filename.split(".csv")[0]+"_seller.csv"
        #     elif "B" in metric: filename=filename.split(".csv")[0]+"_buyer.csv"

        # elif metric=="": metric_folder=""

        df=pd.read_csv(filename, header=None)
        # df=pd.read_csv(join(data_folder_and_subfolder,metric_folder,filename), header=None)

    elif "last" in experiment_part:
        def string_list_to_array(string:str, element_type=int):
            return np.asarray([element_type(_) for _ in string.replace("[","").replace("]","").split(", ")])
            # return np.asarray(re.search("[0-9]+", string).group(0))
        # if metric=="items": metric_folder="items_evolution"
        # elif metric=="rewards": metric_folder="rewards_evolution"
        # elif metric=="" and "evolution" in filename:
        #     splitted_filename=filename.split(".csv")[0].split("/")
        #     if data_folder_and_subfolder=="":
        #         data_folder_and_subfolder="/".join(splitted_filename[:-2])
        #     metric_folder="items_evolution" if "item" in filename else "rewards_evolution"
        #     filename=splitted_filename[-1]+".csv"

        n_last_part=float(re.findall(r"[-+]?(?:\d*\.*\d+)", experiment_part)[0])
        if n_last_part>=1: n_last_part/=100
        n_last_part=1-n_last_part

        # df=pd.read_csv(join(data_folder_and_subfolder,metric_folder,filename))
        df=pd.read_csv(filename)

        col_labels=df.columns.to_list()
        experiment_runs=df[col_labels[0]].unique()
        df_list=[]
        for run in experiment_runs:
            run_rows=df.loc[lambda df: df[col_labels[0]] == run].iloc[:,-1]
            last_run_row=string_list_to_array(run_rows.iloc[-1],element_type=int if "item" in metric else float)
            start_last_part_run_row=string_list_to_array(run_rows.iloc[int(n_last_part*len(run_rows))],
                                                            element_type=int if "item" in metric else float)
            delta_run_rows=last_run_row-start_last_part_run_row
            df_list.append(delta_run_rows)
        df=pd.DataFrame(df_list)

    elif experiment_part=="steps":
        def string_list_to_array(string:str, element_type=int):
            return np.asarray([element_type(_) for _ in string.replace("[","").replace("]","").split(", ")])
        # if metric=="items": metric_folder="items_evolution"
        # elif metric=="rewards": metric_folder="rewards_evolution"

        df=pd.read_csv(filename)
        # df=pd.read_csv(join(data_folder_and_subfolder,metric_folder,filename))

        col_labels=df.columns.to_list()
        df_list=[]
        for _,row in df.iterrows():
            row_list=string_list_to_array(row[col_labels[-1]])
            new_row=[row[col_labels[0]],row[col_labels[1]],*row_list]
            df_list.append(new_row)
        new_col_labels=col_labels[:-1]+[f"{metric}_{robot_id}" for robot_id in range(len(row_list))]
        df=pd.DataFrame(df_list,columns=new_col_labels)

    if not noise_group=="all" or noise_group=="":
        n_r=len(df.columns)
        n_h, _, _, _, _, _, _, noise_params=params_from_filename(filename,compact_format=True)
        n_h=int(n_h)
        sab_performance=noise_params[2]
        n_d=n_r-n_h
        if sab_performance=="avg":
            if "good" in noise_group:
                df=df.iloc[:,:n_h//2+(1 if n_d==0 else 0)]
            elif "bad" in noise_group:
                df=df.iloc[:,n_h//2+(1 if n_d==0 else 0):n_h]
        elif sab_performance=="perf":
            if "good" in noise_group:
                df=df.iloc[:,:n_r//2-n_d+1]
            elif "bad" in noise_group:
                df=df.iloc[:,n_r//2-n_d+1:n_h]
        if "dish" in noise_group or 'sab' in noise_group:
            df=df.iloc[:,n_h:]

    if post_processing is not None:
        #NOTE RETURN TYPE: pandas.Series
        FUN_DICT={"sum":np.sum,"mean":np.mean,"std":np.std,"median":np.median,"min":np.min,"max":np.max}
        items,function=post_processing.split("-")
        if items=="row" or "exp" in items: axis=1
        elif items=="col" or "rob" in items: axis=0
        elif items=="all" or items=="both":
            df=df.apply(FUN_DICT[function],axis=0)
            df=FUN_DICT[function](df)
            df=pd.Series(df)
            return df
        df=df.apply(FUN_DICT[function],axis=axis)
    return df


#TODO TEMPLATE
def filenames_list_for_plotting(
                                data_folder,
                                experiment="",
                                metric="",
                                n_robots=25,
                                n_honests=[25,24,22,],
                                behaviors=["n","s","r","Nv","t","w"],
                                behavior_params_experiments=dict(),
                                combine_strategies=["waa"],
                                payment_systems=["P","NP"],
                                reputation_stake_list=["RS","NRS"],
                                noise_mu=0.0051,
                                noise_range=0.1,
                                # saboteur_performance=["avg","perf"],
                                noise_sampling_mu=0.05,
                                noise_sampling_sd=0.05,
                                noise_sd=0.05,
                                ):
    uniform_avg_noise_params_values=[noise_mu,noise_range,"avg"]
    uniform_perf_noise_params_values=[noise_mu,noise_range,"perf"]
    bimodal_noise_params_values=[noise_sampling_mu,noise_sampling_sd,noise_sd]
    RELEVANT_NOISE_TYPE="uniform"
    RELEVANT_NOISE_PARAMS=uniform_avg_noise_params_values
    filenames_list=[]
    #TODO: ADAPTIVE ORDER OF PARAMS TO CYCLE ON
    for behavior_initials in behaviors:
        for behavior_params_values in behavior_params_experiments[behavior_initials]:
            for n_honest in n_honests:
                for payment_system in payment_systems:
                    for reputation_stake in reputation_stake_list:
                        for combine_stategy_initials in combine_strategies:
                            lie_angle=0 if n_honest==n_robots else 90

                            behavior_params_text=""
                            for v,p in zip(behavior_params_values,BEHAVIOR_PARAMS_DICT[behavior_initials]):
                                behavior_params_text+=f"{v} {PARAMS_NAME_DICT[p]},"
                            #TODO FORMAT OF filenames
                            filenames=[ filename_from_params(n_honest,
                                                    behavior_initials,
                                                    combine_stategy_initials,
                                                    payment_system,
                                                    reputation_stake,
                                                    lie_angle,
                                                    behavior_params_values,
                                                    RELEVANT_NOISE_TYPE,
                                                    RELEVANT_NOISE_PARAMS)
                                    ]
                            filenames=[data_folder+experiment+"/"+SUB_FOLDERS_DICT[behavior_initials]+"/"+metric+"/"+filename+".csv" for filename in filenames]
                            filenames_list.append(filenames)
    return filenames_list


#######################################################################################################################
#######################################################################################################################
########################################## BASE PLOTTING FUNCTIONS ####################################################
def noise_level(
                number_agents=25,
                number_saboteurs=3,
                noise_average=0.05,
                noise_range=0.05,
                saboteurs_noise="", # bimodal:"", "average", "perfect"
                random_switch=False,
                random_seed=None
            ):
    noise_list=generate_uniform_noise_list(number_agents, number_saboteurs, saboteurs_noise,
                                         noise_average, noise_range,random_switch,random_seed)
    fig, ax = plt.subplots()
    fig.set_size_inches(8,8)
    plt.bar(range(len(noise_list)), noise_list)
    plt.xticks(range(len(noise_list)))
    plt.xlabel("agent id")
    plt.ylabel("noise level")
    plt.xticks(rotation=45)
    noise_list=abs(np.array(noise_list))
    values_below005=((0 < noise_list) & (noise_list<= 0.05)).sum()
    values_between005and01=((0.05 < noise_list) & (noise_list<= 0.1)).sum()
    values_between01and015=((0.1 < noise_list) & (noise_list<= 0.15)).sum()
    values_between015and02=((0.15 < noise_list) & (noise_list<= 0.2)).sum()
    plt.suptitle(f"agents' assigned noise distribution mean:{noise_average}, range:{noise_range},\n"
    f"{number_saboteurs} {saboteurs_noise} noise level saboteurs (ids: {[i for i in range(number_agents-number_saboteurs,number_agents)]})\n"
    f"values in [0,0.05]: {values_below005}, [0.05,0.1]: {values_between005and01}, [0.1,0.15]: {values_between01and015}, [0.15,0.2]: {values_between015and02}\n"
    "(original distribution N(0.05,0.05): [0,0.05]: 12, [0.05,0.1]: 9, [0.1,0.15]: 3, [0.15,0.2]: 1)")
    # plt.ion()
    plt.show()
    # plt.pause(0.001)


def noise_vs_items(
                    filenames=[],
                    # data_folder="../data/reputation/",
                    # metric="items_evolution",
                    # saboteurs_noise="",
                    experiments_labels=[],
                    title="",
                    ylabel="",
                    by=1,
                    multi_plot=False,
                    save_plot=False,
                    save_folder="../plots/",
                    save_name="noise_vs_items",
                ):
    '''
    :param filenames: list of filenames to compare,
                    if empty all the files in the folder are fetched
    :param saboteurs_noise: the mode the noise was generated. Accepted values:
                            "bimodal","b": agents have random noise. Otherwise is fixed and
                            "average","a": saboteurs have average noise among all,
                            "perfect","p": saboteurs have lowest noise among all.
    :param multi_plot: if True, .show() performed outside, after creation of all plots
    '''
    BASE_BOX_WIDTH=5
    BASE_BOX_HEIGHT=8
    n_boxes=len(filenames)// by
    fig, axs = plt.subplots(by, n_boxes, sharey=True)
    fig.set_size_inches(BASE_BOX_WIDTH*n_boxes,BASE_BOX_HEIGHT)

    # if metric!="":
    #     data_folder+=f"{metric}/"

    for i,f in enumerate(filenames):
        # if not data_folder=="" and not data_folder==None:
        #     f=f"{data_folder}{f}"
        df=pd.read_csv(f, header=None)
        if len(filenames)>1:
            sns.boxplot(df,ax=axs[i]).set()#xlabel="agent id")
            axs[i].set_xlabel(experiments_labels[i])
        else:
            sns.boxplot(df,ax=axs).set()#xlabel="agent id")
            axs.set_xlabel(experiments_labels)
    plt.suptitle(f"{title}")
    fig.supylabel(f"{ylabel}")
    # fig.supxlabel("agent id")
    sns.despine(offset=0, trim=True)
    for ax in axs:
        ax.tick_params(labelrotation=45)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda x, _: int(x)))
    if 'item' in ylabel: plt.ylim(0,25)
    else: plt.ylim(0,55)

    if not multi_plot:plt.show()
    if save_plot:plt.savefig(f"{save_folder}/{save_name}.png", bbox_inches='tight')


def performance_with_quality(
                        filenames,
                        experiment_part="whole",
                        performance_index="items",
                        pair_plot=True,
                        quality_index="transactionsS",#"reward"
                        multi_quality=True,
                        title="",
                        x_labels=[],
                        show_dishonests=True,
                        multi_plot=False,
                        save_plot=False,
                        save_folder="",
                        save_name="performance_with_quality",
                        ):
    '''
    This method prints a sequence of given boxplots, each one representing a different behaviour.
    On the left y axis, the value of the performance is represented.
    Additionally, on the right y axis, the value of the quality index is represented.

    :param filenames: list of filenames to be plotted. Required format: [filename1, filename2, ...]

    :param performance_index: the performance index to be plotted. As for now, only "items" is supported.

    : pair_plot: if True, second performance index will be plotted in a paired subplot. Default: False.
        As for now, it primary performance metric are items, rewards will be paired, and viceversa.

    :param quality_index: the quality index to be plotted. Automatically fetced based on filenames.
            Required format: [quality_measure]-[quality_function]
        quality_measure: the quality measure to be plotted. Supported values:
         -"trans(actions)": will plot the ratio between a function of both completed and attempted transactions.
           If "trans(actions)C" is specified, will use combined/completed; otherwise attempted/completed.
          "reward(s)": will plot a function of the rewards
        quality_function: supported values: "sum", "mean", "median", "max", "min", "std". "median" by default.

    :param show_dishonests: toggle separate boxplot for dishonests agents performance. Default: True

    _param multi_quality: in this case, in addition to median quality index, 3 more indices are plotted:
        -quality for the group of "good" robots alone (i.e. with noise level below average),
        -quality for the group of "bad" robots alone (i.e. with noise level above average),
        -quality for the group of dishonets robots alone.
        The used quality index is the same as the one used for the median quality index.
    '''
    BASE_BOX_WIDTH=16
    BASE_BOX_HEIGHT=7
    base_title="Performance of Reputation Systems"
    if not pair_plot:
        n_subplots=1
    else:
        n_subplots=2
    fig, axs = plt.subplots(1, n_subplots, squeeze=False if n_subplots==1 else True)
    if not pair_plot:axs=axs[0]

    if not quality_index=="":
        try:
            quality_index, quality_function=quality_index.split("-")
        except ValueError:
            quality_function="median"

    for j in range (n_subplots):
        current_filenames=filenames if not pair_plot else filenames[j]
        
        if show_dishonests:
            honest_list=[]
            dishonest_list=[]
        else:
            performance_list=[]
        quality_list=[]
        if multi_quality:
            good_quality_list=[]
            bad_quality_list=[]
            dishonest_quality_list=[]

        # if not x_labels:
        #     x_labels=[]
        #     auto_x_labels=True
        # else:auto_x_labels=False

        for i,f in enumerate(current_filenames):
            if not f.endswith(".csv"):f+=".csv"
            splitted_filename=f.split('.csv')[0].split("/")
            df=dataframe_from_csv(f,experiment_part=experiment_part)
            n_honest, honest_behavior, _, payment,reputation_stake, _, behaviour_params, noise_params=params_from_filename(f,compact_format=True)
            n_honest=int(n_honest)
            n_robots=len(df.columns)
            n_dishonest=n_robots-n_honest
            saboteur_performance=noise_params[2]

            # if auto_x_labels:
            #     behavior_params_text=""
            #     for v,p in zip(behaviour_params,BEHAVIOR_PARAMS_DICT[honest_behavior]):
            #         behavior_params_text+=f"{v} {p},\n"
            #     x_labels.append(f"{BEHAVIORS_NAME_DICT[honest_behavior]}\n"
            #     f"{behavior_params_text}"
            #     f"{'no ' if payment=='NP' else ''}penalis.")

            if show_dishonests:
                df_honest=df.iloc[:,:int(n_honest)]
                df_dishonest=df.iloc[:,int(n_honest):]
                df_honest['behavior']=BEHAVIORS_NAME_DICT[honest_behavior]
                df_dishonest['behavior']=f"Saboteur {BEHAVIORS_NAME_DICT[honest_behavior]}"
                df_honest['plot_order']=i
                df_dishonest['plot_order']=i
                honest_list.append(df_honest)
                dishonest_list.append(df_dishonest)
            else:
                df['behavior']=BEHAVIORS_NAME_DICT[honest_behavior]
                df['plot_order']=i
                performance_list.append(df)

            if quality_index:
                if "trans" in quality_index:
                    if "C" in quality_index:
                        numerator_quality="completed"
                    else:
                        numerator_quality="combined"
                    # denominator_quality="attempted"
                    denominator_quality="validated"

                    if "B" in quality_index:
                        numerator_quality+="_buyer"
                        denominator_quality+="_buyer"
                    elif "S" in quality_index:
                        numerator_quality+="_seller"
                        denominator_quality+="_seller"

                    fq_num="/".join(splitted_filename[:-2]+["transactions"]+splitted_filename[-1:])+f"_{numerator_quality}.csv"
                    fq_den="/".join(splitted_filename[:-2]+["transactions"]+splitted_filename[-1:])+f"_{denominator_quality}.csv"
                    df_q_num=dataframe_from_csv(fq_num,post_processing="all-"+quality_function)
                    df_q_den=dataframe_from_csv(fq_den,post_processing="all-"+quality_function)
                    df_quality=100*df_q_num/df_q_den

                    if multi_quality:
                        df_q_num=dataframe_from_csv(fq_num,post_processing="col-"+quality_function)
                        df_q_den=dataframe_from_csv(fq_den,post_processing="col-"+quality_function)

                        if saboteur_performance=="avg":
                            good_slice=n_honest//2+(1 if n_dishonest==0 else 0)
                        elif saboteur_performance=="perf":
                            good_slice=n_robots//2-n_dishonest+1
                        bad_slice=-n_dishonest if n_dishonest>0 else None
                        #TODO narrower good/bad groups
                        # narrow_slice=0#BUG  empty color sequence error
                        df_q_good_num=df_q_num.iloc[:good_slice]#-narrow_slice]
                        df_q_good_den=df_q_den.iloc[:good_slice]#-narrow_slice]
                        df_q_bad_num=df_q_num.iloc[good_slice:bad_slice]#-narrow_slice:bad_slice+narrow_slice]
                        df_q_bad_den=df_q_den.iloc[good_slice:bad_slice]#-narrow_slice:bad_slice+narrow_slice]
                        df_q_good=100*df_q_good_num/df_q_good_den
                        df_q_bad=100*df_q_bad_num/df_q_bad_den

                        if n_dishonest>0:
                            df_q_dishonest_num=df_q_num.iloc[n_honest:]
                            df_q_dishonest_den=df_q_den.iloc[n_honest:]
                            df_q_dishonest=100*df_q_dishonest_num/df_q_dishonest_den
                
                elif "reward" in quality_index:
                    fq="/".join(splitted_filename[:-2]+["rewards"]+splitted_filename[-1:])+".csv"
                    df_quality=dataframe_from_csv(fq,post_processing="all-"+quality_function)

                    if multi_quality:
                        df_multi_q=dataframe_from_csv(fq,post_processing="col-"+quality_function)
                        df_q_good=df_multi_q.iloc[:int(n_honest)//2]
                        df_q_bad=df_multi_q.iloc[int(n_honest)//2:int(n_honest)]
                        if n_dishonest>0:
                            df_q_dishonest=df_multi_q.iloc[int(n_honest):]

                df_quality=pd.DataFrame(df_quality,columns=[quality_index])
                df_quality['behavior']="Q2"+BEHAVIORS_NAME_DICT[honest_behavior]
                df_quality['plot_order']=i
                quality_list.append(df_quality)

                if multi_quality:
                    df_q_good=pd.DataFrame(df_q_good,columns=[quality_index])
                    #NOTE if quality_list.append() is used, every quality behavior: "Qi"+B must be different
                    df_q_good['behavior']="Q4"+BEHAVIORS_NAME_DICT[honest_behavior]
                    df_q_good['plot_order']=i
                    df_q_bad=pd.DataFrame(df_q_bad,columns=[quality_index])
                    df_q_bad['behavior']="Q4"+BEHAVIORS_NAME_DICT[honest_behavior]
                    df_q_bad['plot_order']=i
                    good_quality_list.append(df_q_good)
                    bad_quality_list.append(df_q_bad)
                    if n_dishonest>0:
                        df_q_dishonest=pd.DataFrame(df_q_dishonest,columns=[quality_index])
                        df_q_dishonest['behavior']="QD"+BEHAVIORS_NAME_DICT[honest_behavior]
                        df_q_dishonest['plot_order']=i
                        dishonest_quality_list.append(df_q_dishonest)
                    #TODO NOTE following case: use single boxplot for median+specific quality
                    # quality_list.append(df_q_good)
                    # quality_list.append(df_q_bad)
                    # quality_list.append(df_q_dishonest)

        if show_dishonests:
            data_honest=pd.concat(honest_list)
            data_dishonest=pd.concat(dishonest_list)
            # performance_max=max(max(data_dishonest.iloc[:,int(n_honest):].apply(np.max)),
            #                       max(data_honest[:,:int(n_honest)].apply(np.max)))

            #TODO newcomers data joined with dishonests
            # data_newcomers=
            # data_newcomers['behavior']="NEW"+BEHAVIORS_NAME_DICT[honest_behavior]
            # data_small=pd.concat([data_newcomers,data_dishonest])

            #big and small paired boxplots
            sns.boxplot(data=pd.melt(data_honest, id_vars=['behavior','plot_order']),
                            x='plot_order',y='value', hue='behavior',palette=BEHAVIOUR_PALETTE,
                            linewidth=1, dodge=False,width=.5,ax=axs[j])#
            # sns.boxplot(data=pd.melt(data_small, id_vars=['behavior','plot_order']),
            #                 x='plot_order',y='value', hue='behavior',palette=BEHAVIOUR_PALETTE,
            #                 linewidth=1.65, dodge=True, saturation=0.85, width=0.7, ax=axs[j])
            sns.boxplot(data=pd.melt(data_dishonest, id_vars=['behavior','plot_order']),
                            x='plot_order',y='value', hue='behavior',palette=BEHAVIOUR_PALETTE,
                            linewidth=1.65, dodge=True, saturation=0.85, width=0.5, ax=axs[j])
            
            #BUG same size paired boxplots label not aligned
            # data_full=pd.concat([data_honest,data_dishonest])
            # sns.boxplot(data=pd.melt(data_full, id_vars=['behavior','plot_order']),
            #                 x='plot_order',y='value', hue='behavior',palette=BEHAVIOUR_PALETTE,
            #                 linewidth=1, dodge=True,width=2.5)
        else:
            data_performance=pd.concat(performance_list)
            sns.boxplot(data=pd.melt(data_performance, id_vars=['behavior','plot_order']),
                            x='plot_order',y='value', hue='behavior',palette=BEHAVIOUR_PALETTE,
                            linewidth=1, dodge=False,width=.5,ax=axs[j])
            # performance_max=max(data_performance.iloc[:,:24].apply(np.max))

        #TODO AX2 YTICKS look like  "-" signs\

        if not quality_index=="":
            data_quality=pd.concat(quality_list)
            if multi_quality:
                data_quality_good=pd.concat(good_quality_list)
                data_quality_bad=pd.concat(bad_quality_list)
                if n_dishonest>0:
                    data_quality_dishonest=pd.concat(dishonest_quality_list)
                
            if "trans" in quality_index:
                quality_label=f"{numerator_quality}/{denominator_quality} transactions"
                #TODO if multi_plot:pass

            elif "reward" in quality_index:
                quality_label="reward\n(each value >0)"
                #TODO if multi_plot:pass

            quality_label=f"{quality_function} {quality_label}"

            if j>0 or not pair_plot:
                ax2=axs[j].twinx()
                if 'trans' in quality_index:
                    ax2.yaxis.set_major_formatter(mtick.PercentFormatter())

                if not pair_plot or j>0:
                    if multi_quality:
                        #matplotlib markers https://matplotlib.org/3.1.0/api/markers_api.html
                        sns.pointplot(data=pd.melt(data_quality_good,id_vars=['behavior','plot_order']),palette=BEHAVIOUR_PALETTE,
                                        x='plot_order',y='value', hue='behavior',ax=ax2,markers="s",join=False,errorbar=None)
                                            
                    sns.pointplot(data=pd.melt(data_quality,id_vars=['behavior','plot_order']),palette=BEHAVIOUR_PALETTE,
                                    x='plot_order',y='value', hue='behavior',
                                    markers="o",
                                    # markers=["*","+","o","."]*5,
                                    ax=ax2,join=False,errorbar=None)

                    if multi_quality:#NOTE improves visibility of small dot
                        sns.pointplot(data=pd.melt(data_quality_bad,id_vars=['behavior','plot_order']),palette=BEHAVIOUR_PALETTE,
                                        x='plot_order',y='value', hue='behavior',ax=ax2,markers="^",join=False,errorbar=None)
                        if n_dishonest>0:
                            warnings.filterwarnings( "ignore", module = "seaborn\..*" )#ignore color of "x" warning
                            sns.pointplot(data=pd.melt(data_quality_dishonest,id_vars=['behavior','plot_order']),palette=BEHAVIOUR_PALETTE,
                                            x='plot_order',y='value', hue='behavior',ax=ax2,markers="x",join=False,errorbar=None)
                            warnings.filterwarnings( "default", module = "seaborn\..*" )

                    ax2.legend().set_visible(False)

                if not title:title=base_title+" with Quality Index"
            else:
                axs[j].legend(title="(red boxplots: dishonests)", loc="lower left", labels=[])
                if not title:title=base_title
                ax2=None

        plt.sca(axs[j])
        plt.legend().set_visible(False)
        plt.xticks(np.arange(0,len(current_filenames)),x_labels[:len(current_filenames)])
        if "items" in performance_index:
            if j==0:performance_label="items collected"
            else: performance_label="reward"
        else:
            if j==0:performance_label=performance_index
            if j>0: performance_label="items collected"
        plt.ylabel(performance_label)
        plt.ylim(-1 if 'item' in performance_label else None,
                        35 if 'item' in performance_label and experiment_part=='whole' else \
                        14 if 'item' in performance_label and 'last' in experiment_part \
                            else None)#int(1.25*performance_max))
        if not pair_plot:
            ax2.set_ylabel(quality_label)
        elif j>0:ax2.set_ylabel(quality_label)

        axs[j].set_xlabel('')
    fig.set_size_inches(BASE_BOX_WIDTH*n_subplots,BASE_BOX_HEIGHT+1)
    sns.despine(fig,trim=False, )
    fig.suptitle(title,fontweight="bold")

    if not multi_plot and not save_plot:plt.show()
    if save_plot:
        plt.savefig(f"{join(save_folder,save_name)}.png", bbox_inches='tight')
        plt.close()


#####################################################################################
# -----------------------EXPERIMENTS PLOTTING FUNCTIONS---------------------------------- #
def compare_behaviors_performance_quality(
                                        data_folder,
                                        experiment="",
                                        experiment_part="whole",
                                        performance_metric="",
                                        pair_plot=False,
                                        short_x_labels=False,
                                        quality_index="",
                                        multi_quality=False,
                                        show_dishonests=False,
                                        auto_xlabels=True,
                                        n_robots=25,
                                        n_honests=[25,24,22,],
                                        behaviours=[],
                                        behavior_params_experiments=dict(),
                                        combine_stategies=["waa"],
                                        payment_systems=["P","NP"],
                                        reputation_stake_list=[True,False],
                                        noise_type_list=["uniform"],
                                        noise_mu_list=[0.051],
                                        noise_range_list=[0.1],
                                        saboteur_performance_list=["avg","perf"],
                                        compare_best_of=False,
                                        multi_plot=True,
                                        save_plot=False,
                                        save_folder=""
                                    ):
    '''
    This function plots the performance of different combinations of same behaviour, or 
    behaviours, wrt a certain metric.
    Performance is showed on the y axis, different behaviours on the x axis.
    Additionally, a second y axis is added to show the quality of the behaviours.
    As reference, each plot will compare always results for naive, sceptical+{P, NP}.
    The funciton will automatically fetch data from the data_folder and retrieve the
    experiment. Moreover, only the interesting part of it can be loaded.

    :param data_folder: folder where the data is stored.

    :param experiment: experiment  subfolder to choose the data from.

    :param experiment_part: if data should be selected from the whole experiment data set,
        or a specific part of it. Refer to dataframe_from_csv for more info.

    :param performance_metric: metric to plot. Permitted values are:
            "items";
            "rewards".

    :param quality_metric: additional metric for quality. Permitted values are:
        "" or None: no quality showed;
        "completed_rate": combined/attempted transactions;
        "median_reward": median reward of all agents;

    :param n_robots: number of robots in the experiment.

    :param n_honests: list of honest robots to retrieve experiments.

    :param behaviors: list of behaviours to plot. Required format: initials

    :param behavior_params_experiments: dictionary of behaviour params combinations to use.

    :param payment_systems: list of payment systems to plot.

    :param noise_mu: average noise to use.

    :param noise_range: range of noise to use.

    :param saboteur_performance: list of saboteur performances to plot.

    :param multi_plot: if True, .show() performed outside, after creation of all plots.

    :param save_plot: if True, the plot is saved in the save_folder.

    :param save_folder: folder where the plot is saved.
    '''
    if multi_plot:fig_count=0

    if save_plot and not os.path.exists(join(save_folder,experiment)):
            os.makedirs(join(save_folder,experiment),exist_ok=True)

    if 'item' in performance_metric:
        if experiment_part=="whole":
            performance_folder="items_collected"
            # if pair_plot:secondary_performance_folder="rewards"
        else:
            performance_folder="items_evolution"
            # if pair_plot:secondary_performance_folder="rewards_evolution"
        if pair_plot:secondary_performance_folder="rewards"
    elif 'reward' in performance_metric:
        performance_folder="rewards"
        if experiment_part=="whole":
            # performance_folder="rewards"
            if pair_plot:secondary_performance_folder="items_collected"
        else:
            # performance_folder="rewards_evolution"
            if pair_plot:secondary_performance_folder="items_evolution"

    for n_honest in n_honests:
        lie_angle=0 if n_honest==n_robots else 90
        for noise_type in noise_type_list:
            for saboteur_performance in saboteur_performance_list:
                for noise_mu in noise_mu_list:
                    for noise_range in noise_range_list:
                        noise_params_values=[noise_mu,noise_range,saboteur_performance]
                        
                        if compare_best_of: best_list=[];best_labels=[]
                        for payment_system in payment_systems:
                            for reputation_stake in reputation_stake_list:
                                if reputation_stake and payment_system=="NP":continue
                                for behavior_initials in behaviours:
                                    for combine_stategy_initials in combine_stategies:
                                        if save_plot:
                                            behav_save_folder=join(save_folder,experiment,performance_metric,SUB_FOLDERS_DICT[behavior_initials])
                                            if not os.path.exists(behav_save_folder):os.makedirs(behav_save_folder,exist_ok=True)
                                        filenames=[
                                            filename_from_params(n_honest,"n", "waa",
                                                                "NP","NRS",lie_angle,
                                                                [],
                                                                noise_type,noise_params_values),
                                            # filename_from_params(n_honest,"n", "waa",
                                            #                     "P","NRS",lie_angle,
                                            #                     [],
                                            #                     noise_type,noise_params_values),
                                            # filename_from_params(n_honest,"s", "waa",
                                            #                     "NP","NRS",lie_angle,
                                            #                     [0.25],
                                            #                     noise_type,noise_params_values),
                                            filename_from_params(n_honest,"s", "waa",
                                                                "P","NRS",lie_angle,
                                                                [0.25],
                                                                noise_type,noise_params_values),
                                            ]
                                        BASIC_BEHAV_LEN=len(filenames)
                                        filenames=[join(data_folder,experiment,SUB_FOLDERS_DICT[b_i],\
                                            performance_folder,f)+(".csv" if not f.endswith(".csv") else "")\
                                                for f,b_i in zip(filenames,(['n','s'] if BASIC_BEHAV_LEN==2 else ['n','n','s','s']))]

                                        if not auto_xlabels:
                                            if BASIC_BEHAV_LEN==4: x_labels=["Naive\nno penalisation","Naive\npenalisation","Sceptical\nno penalisation","Sceptical\npenalisation"]
                                            elif BASIC_BEHAV_LEN==2: x_labels=["Naive\nno penalisation","Sceptical\npenalisation"]
                                            if short_x_labels:
                                                if BASIC_BEHAV_LEN==4: x_labels=["n\nNP","n\nP","s\nNP","s\nP"]
                                                elif BASIC_BEHAV_LEN==2: x_labels=["n\nNP","s\nP"]
                                        else: x_labels=[]

                                        for behavior_params_values in behavior_params_experiments[behavior_initials]:
                                            f=filename_from_params(n_honest,behavior_initials, 
                                                                    combine_stategy_initials,
                                                                    payment_system,
                                                                    reputation_stake,
                                                                    lie_angle,
                                                                    behavior_params_values,
                                                                    "uniform",noise_params_values)
                                            f=join(data_folder,experiment,SUB_FOLDERS_DICT[behavior_initials],\
                                            performance_folder,f)+(".csv" if not f.endswith(".csv") else "")

                                            if CONFIG_FILE.PRUNE_FILENAMES  and \
                                                    ((CONFIG_FILE.PRUNE_NOT_BEST and is_best_param_combination(f)) or \
                                                    (not CONFIG_FILE.PRUNE_NOT_BEST and not is_bad_param_combination(f))) or \
                                            not CONFIG_FILE.PRUNE_FILENAMES:
                                                filenames.append(f)
                                                if not auto_xlabels:
                                                    behavior_params_text=""
                                                    if not short_x_labels:
                                                        behav_label=BEHAVIORS_NAME_DICT[behavior_initials]
                                                        for v,p in zip(behavior_params_values,BEHAVIOR_PARAMS_DICT[behavior_initials]):
                                                            behavior_params_text+=f"{v} {p},\n"
                                                        penalisation_text=f"{'no ' if payment_system=='NP' else ''}penalis."
                                                    else:
                                                        behav_label=behavior_initials
                                                        for v in behavior_params_values:
                                                            behavior_params_text+=f"{v},\n"   
                                                        penalisation_text=f"{payment_system}"
                                                    x_label=f"{behav_label}\n"\
                                                    f"{behavior_params_text}"\
                                                    f"{penalisation_text}"
                                                    x_labels.append(x_label)
                                                if compare_best_of and is_best_param_combination(f):
                                                    best_list.append(f)
                                                    best_labels.append(x_label)

                                        if 'last' in experiment_part:
                                            n_last_part=float(re.findall(r"[-+]?(?:\d*\.*\d+)", experiment_part)[0])
                                            if n_last_part<=1: n_last_part*=100
                                            part_text=f"last {n_last_part}% of "
                                        else: part_text="whole "
                                        stable_part_title=f" for the {part_text}experiment\n"
                                        title=f"Performance comparison for {BEHAVIORS_NAME_DICT[behavior_initials]} behavior,\n"\
                                            f"{'with quality index ,' if quality_index else ''}{stable_part_title}"\
                                            f"for {n_honest} honests, {lie_angle}° lie angle,\n"\
                                            f"{noise_mu} mean noise, {noise_range} noise range, {'perfect' if saboteur_performance=='perf' else 'average'} saboteur performance"\
                                            # f"{COMBINE_STRATEGY_NAME_DICT[combine_stategy_initials]} combine strategy\n"\
                                        if reputation_stake:title+=",   \nwith Staking based on reputation"
                                        save_name=f"{n_honest}_{behavior_initials}_{payment_system}_{lie_angle}_{noise_mu}_{noise_range}_{saboteur_performance}"
                                        
                                        if not len(filenames)>BASIC_BEHAV_LEN:continue

                                        if pair_plot:
                                            secondary_filenames=[f.replace(performance_folder,secondary_performance_folder) for f in filenames]
                                            filenames=[filenames,secondary_filenames]
                                        performance_with_quality(
                                                                filenames,
                                                                experiment_part=experiment_part,
                                                                performance_index=performance_metric,
                                                                pair_plot=pair_plot,
                                                                quality_index=quality_index,
                                                                multi_quality=multi_quality,
                                                                title=title,
                                                                x_labels=x_labels,
                                                                show_dishonests=show_dishonests if n_honest<n_robots else False,
                                                                multi_plot=multi_plot,
                                                                save_plot=save_plot,
                                                                save_folder=behav_save_folder if save_plot else "",
                                                                save_name=save_name,
                                                                )
                                        if multi_plot:fig_count+=1

                        if compare_best_of and len(best_list)>0:
                            best_save_name=f"best_{n_honest}_{lie_angle}_{noise_mu}_{noise_range}_{saboteur_performance}"
                            #NOTE no need to order, for how the loop is built
                            # best_list=(filenames[:4] if not pair_plot else filenames[0][:4])\
                            #             +[fb for b_i in behaviours for fb in best_list \
                            #                 if params_from_filename(fb,compact_format=True)[1]==b_i]
                            best_list=(filenames[:BASIC_BEHAV_LEN] if not pair_plot else filenames[0][:BASIC_BEHAV_LEN])+best_list
                            # if not len(best_list)>BASIC_BEHAV_LEN:continue 
                            #TODO order labels alongside the list
                            best_labels=x_labels[:BASIC_BEHAV_LEN]+best_labels
                            if pair_plot:
                                best_list=[best_list,[f.replace(performance_folder,secondary_performance_folder) for f in best_list]]
                            title=f"Performance comparison for best combination of all behaviors,\n"\
                                            f"{'with quality index ,' if quality_index else ''}{stable_part_title}"\
                                            f"for {n_honest} honests, {lie_angle}° lie angle,\n"\
                                            f"{noise_mu} mean noise, {noise_range} noise range, {'perfect' if saboteur_performance=='perf' else 'average'} saboteur performance"\
                                            # f"{COMBINE_STRATEGY_NAME_DICT[combine_stategy_initials]} combine strategy\n"\
                            if reputation_stake:title+=",   \nwith Staking based on reputation"
                                        
                            performance_with_quality(
                                                    best_list,
                                                    experiment_part=experiment_part,
                                                    performance_index=performance_metric,
                                                    pair_plot=pair_plot,
                                                    quality_index=quality_index,
                                                    multi_quality=multi_quality,
                                                    title=title,
                                                    x_labels=best_labels,
                                                    show_dishonests=show_dishonests if n_honest<n_robots else False,
                                                    multi_plot=multi_plot,
                                                    save_plot=save_plot,
                                                    save_folder=join(save_folder,experiment,performance_metric) \
                                                        if save_plot else "",
                                                    save_name=best_save_name,
                                                    )
                            if multi_plot:fig_count+=1

    if multi_plot:
        if not save_plot:plt.show()
        else:print(f"saved {fig_count} figures in {join(save_folder,experiment)}")
  

def bimodal_uniform_noise_comparison(
                                        data_folder,
                                        experiment="",
                                        metric="",
                                        n_robots=25,
                                        n_honests=[25,24,22,],
                                        behaviors=["n","s","r","Nv","t","w"],
                                        behavior_params_experiments=dict(),
                                        combine_strategies=["waa"],
                                        payment_systems=["P","NP"],
                                        reputation_stake_list=["RS","NRS"],
                                        noise_mu=0.051,
                                        noise_range=0.1,
                                        saboteur_performance=["avg","perf"],
                                        noise_sampling_mu=0.05,
                                        noise_sampling_sd=0.05,
                                        noise_sd=0.05,
                                        multi_plot=True,
                                        save_plot=False,
                                        save_folder=""
                                ):
    uniform_avg_noise_params_values=[noise_mu,noise_range,"avg"]
    uniform_perf_noise_params_values=[noise_mu,noise_range,"perf"]
    bimodal_noise_params_values=[noise_sampling_mu,noise_sampling_sd,noise_sd]

    if multi_plot:fig_count=0
    if save_plot and not os.path.exists(save_folder+experiment):
        os.makedirs(save_folder+experiment)
    for behavior_initials in behaviors:
        behav_save_folder=join(save_folder,experiment,metric,SUB_FOLDERS_DICT[behavior_initials])
        if not os.path.exists(behav_save_folder):os.makedirs(behav_save_folder,exist_ok=True)
        for behavior_params_values in behavior_params_experiments[behavior_initials]:
            for n_honest in n_honests:
                for combine_strategy_initials in combine_strategies:
                    for payment_system in payment_systems:
                        for reputation_stake in reputation_stake_list:
                            lie_angle=0 if n_honest==n_robots else 90

                            behavior_params_text=""
                            for v,p in zip(behavior_params_values,BEHAVIOR_PARAMS_DICT[behavior_initials]):
                                behavior_params_text+=f"{v} {PARAMS_NAME_DICT[p]},"

                            penalisation=" no" if payment_system=="NP" else ""
                            labels=[f"{lie_angle}° lie angle\nbimodal noise",
                                    f"{lie_angle}° lie angle\nnon b. noise\naverage saboteurs",
                                    f"{lie_angle}° lie angle\nnon b. noise\nperfect saboteurs"]

                            title=f"{BEHAVIORS_NAME_DICT[behavior_initials]} behaviour\n"\
                            f"parameters: {behavior_params_text}\n"\
                            f"{n_honest} honests,{penalisation} penalisation\n"\
                            "different noise models"

                            filenames=[ filename_from_params(n_honest,behavior_initials,
                                                    combine_strategy_initials,
                                                    payment_system,reputation_stake,
                                                    lie_angle,
                                                    behavior_params_values,
                                                    "bimodal",bimodal_noise_params_values,),
                                        filename_from_params(n_honest,behavior_initials,
                                                    combine_strategy_initials,
                                                    payment_system,lie_angle,
                                                    behavior_params_values,
                                                    "uniform",uniform_avg_noise_params_values),
                                        filename_from_params(n_honest,behavior_initials,
                                                    combine_strategy_initials,
                                                    payment_system,lie_angle,
                                                    behavior_params_values,
                                                    "uniform",uniform_perf_noise_params_values)
                                    ]
                            #TODO: test filenames, else remove from list filenames
                            filenames=[join(data_folder,experiment,SUB_FOLDERS_DICT[behavior_initials],metric,filename,".csv") for filename in filenames]

                            save_name=filename_from_params(n_honest,behavior_initials,
                                                    combine_strategy_initials,
                                                    payment_system,lie_angle,
                                                    behavior_params_values,
                                                    "uniform",uniform_avg_noise_params_values)
                            noise_vs_items(filenames,
                                            data_folder=f"",
                                            metric=f"",
                                            experiments_labels=labels,
                                            title=title,
                                            ylabel=metric.replace("_"," "),
                                            multi_plot=multi_plot,
                                            save_plot=save_plot,
                                            save_folder=behav_save_folder,
                                            save_name=save_name
                            )
                            fig_count+=1
    if multi_plot and not save_plot:plt.show()
    fig_count=0


#TODO TEMPLATE
def plot_results(filenames,
                 data_folder="../data/DATA_SUBFOLDER/",
                 metric="items",
                 experiment_part="whole",
                 type_of_plot="behaviour",
                 params_to_iterate_on=None,
                 params_to_generate_labels=[]
                 ):
    '''
    :param filenames: list of filenames to compare.
        if absolute path is passed, data_folder and metric are ignored
        shape must be [[filename1, filename2, ...], [filename1, filename2, ...], ...]
        for type_of_plot="behaviour": [[b11,b12,...],[b21,b22,...],...], will compare bkj for each j,
            producing k subplots, with j elements each
        for type_of_plot="noise": [...,[bKref,bKavg,bKperf],...], will compare b1ref with b1avg and b1perf, for each K,
            producing K different plots, each with 3 subplots, each one with n_robots elements
    :param data_folder: main data folder.
        This is devided in SUBFOLDERS (different experiments,...); each one of this contains folders
        for each tested behaviour (these are automatically retrived by filenames)
        Each behaviour subfolder contains the data from each tested metric.
    :param metric: the metric to plot. Accepted values:
        "items": number of collected items in an experiments
        "reward": reward in an experiments
        wrt the experiment_part, this will load data from items_collected and reward or from
        items_evolution and reward_evolution
    :param experiment_part: decide if use data from the whole experiment or just a part of it. Accepted values:
        "whole": use all the data; this will load data from items_collected and reward
        "lastN", N:int =[50,100] || [0.5,1]: use only the data from the last N% of the experiment;
         this will load data from intems_evolution and reward_evolution
    :param type_of_plot: decide the type of plot to use. Accepted values:
        "behaviour": compares result for same parameters for different behaviours
        "noise": compares different noise levels (==agents ids) for same behaviour and parameters
    :param params_to_iterate_on:  list of parameters to iterate on.
        as for now, this uses the filenames arrays
    :param params_to_generate_labels: list of params of data to include in the legend.
        values must be keys of PARAMS_NAME_DICT
    '''
    #1 GET METRIC
    if experiment_part == "whole":
        if metric=="items": metric="items_collected"
        elif metric=="reward": metric="reward"
    else:
        metric+="_evolution"
        last_part = float(experiment_part[6:])
    #2 CONSTRUCT THE COMPLETE FILENAMES
    #if filenames are absolute paths, ignore data_folder and metric
    # as for now, construct manually using the lists
    # if filenames[0][0][0] != "/":
    #     filenames = [[data_folder + f + "/" + metric + ".csv" \
    #         for f in filenames[i]] for i in range(len(filenames))]

    #3 ITERATE OVER VECTORS

##############################################################################################################
##############################################################################################################
if __name__ == '__main__':
# if __name__ == '__main__':
    pass
    #TODO: create this as a summary from config generation / running
        
        # bimodal_uniform_noise_comparison(data_folder=CONFIG_FILE.DATA_DIR,
        #                                 experiment="",
        #                                 metric="rewards",
        #                                 n_robots=25,
        #                                 n_honests=[25,24],
        #                                 behaviors=["n","s","r","Nv","t","w"],
        #                                 behavior_params_experiments=BEHAV_PARAMS_COMBINATIONS,
        #                                 multi_plot=True,
        #                                 save_plot=False,
        #                                 save_folder=""#CONFIG_FILE.PLOT_DIR
        #                                 )

        # find_best_worst_seeds(filenames=[],
        #                     data_folder="../data/sceptical/",
        #                     metric="items_collected",
        #                     base_seed=5684436,
        #                     amount_to_find=3,
        #                 )

        # print(dataframe_from_csv(filename="22r_waaCS_NP_90LIA_0.3RT_0.051NMU_0.1NRANG_avgSAB.csv",
        #                 data_folder_and_subfolder=join(CONFIG_FILE.DATA_DIR,"FULL_TEST/ranking"),
        #                 metric="items",
        #                 experiment_part="whole",
        #                 noise_group="s",
        #                 post_processing="row-mean"
        #                 ))

    compare_behaviors_performance_quality(
                                            data_folder=CONFIG_FILE.DATA_DIR,
                                            experiment="NO_FORAGING_MARKET",
                                            experiment_part="whole",
                                            # experiment_part="last.33",
                                            performance_metric="items",
                                            pair_plot=False,
                                            short_x_labels=True,
                                            quality_index="transactionsS",
                                            multi_quality=True,
                                            show_dishonests=True,
                                            auto_xlabels=False,
                                            n_honests=[
                                                24,
                                                # 22,
                                                # 25,
                                                # 17,
                                                # 20
                                                ],
                                            behaviours=[
                                                'r',
                                                't' ,
                                                'Nv',
                                                'h'
                                                ],#to compare w/ n+NP,n+P,s+NP,s+P 
                                            behavior_params_experiments=BEHAV_PARAMS_COMBINATIONS,
                                            payment_systems=[
                                                "NP",
                                                "P"
                                                ],
                                            reputation_stake_list=[
                                                                    False,
                                                                    True,
                                                                ],
                                            saboteur_performance_list=[
                                                                    "avg",
                                                                "perf",
                                                                ],
                                        compare_best_of=True,
                                        multi_plot=True,
                                        save_folder=join(CONFIG_FILE.PLOT_DIR,"behav_compar_quality"),
                                        save_plot=0
                                    )
                             
