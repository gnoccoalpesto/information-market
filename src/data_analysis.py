import re
import os
from os.path import join, isfile
import argparse
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick # to plot percentage on axis for matplotlib
from  matplotlib.ticker import FuncFormatter #to force axis to have integer ticks
from matplotlib.cbook import boxplot_stats
import seaborn as sns
import time
import scipy.stats as stats
# from sklearn.cluster import KMeans # type: ignore # pylint: disable=import-error

import config as CONFIG_FILE
from model.environment import generate_uniform_noise_list
from model.behavior import  BEHAVIORS_NAME_DICT, SUB_FOLDERS_DICT, PARAMS_NAME_DICT, \
                        BEHAVIOR_PARAMS_DICT,COMBINE_STRATEGY_NAME_DICT, noise_groups_slices
from info_market import filename_from_params, params_from_filename,\
                    is_bad_param_combination, is_best_param_combination


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
                    'hs':"#9467bd",#5, brown
                    'Rep. Hist. Sceptical':"#8c564b",
                    'Reputation History Sceptical':"#8c564b",
                    'Saboteur Rep. Hist. Sceptical':"#d62728",
                    'Saboteur Reputation History Sceptical':"#d62728",
                    'c':"#7f7f7f",#8, grey
                    'Capitalist':"#7f7f7f",
                    'Saboteur Capitalist':"#d62728",
                    'b':"#bcbd22",#9, yellow
                    'Benchmark':"#bcbd22",
                    'Saboteur Benchmark':"#d62728",
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
                    'Q1hs':"#937860",#5, deep brown
                    'Q1Rep. Hist. Sceptical':"#937860",
                    'Q1Reputation History Sceptical':"#937860",
                    'Q1c':"#8c8c8c",#8, grey deep
                    'Q1Capitalist':"#8c8c8c",
                    'Q1b':"#ccb974",#9, yellow deep
                    'Q1Benchmark':"#ccb974",
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
                    'Q2hs':"#592f0d",#5, dark brown
                    'Q2Rep. Hist. Sceptical':"#592f0d",
                    'Q2Reputation History Sceptical':"#592f0d",
                    'Q2c':"#4c4c4c",#8, grey dark
                    'Q2Capitalist':"#4c4c4c",
                    'Q2b':"#7f6000",#9, yellow dark
                    'Q2Benchmark':"#7f6000",
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
                    'Q3hs':"#9f4800",#5, bright brown
                    'Q3Rep. Hist. Sceptical':"#9f4800",
                    'Q3Reputation History Sceptical':"#9f4800",
                    'Q3c':"#bfbfbf",#8, grey bright
                    'Q3Capitalist':"#bfbfbf",
                    'Q3b':"#ffbf00",#9, yellow bright
                    'Q3Benchmark':"#ffbf00",
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
                    'Q4hs':"#debb9b",#5, pastel brown
                    'Q4Rep. Hist. Sceptical':"#debb9b",
                    'Q4Reputation History Sceptical':"#debb9b",
                    'Q4c':"#e6e6e6",#8, grey pastel
                    'Q4Capitalist':"#e6e6e6",
                    'Q4b':"#ffe6b2",#9, yellow pastel
                    'Q4Benchmark':"#ffe6b2",
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
                    'Q5hs':"#ca9161",#5, colorblind brown
                    'Q5Rep. Hist. Sceptical':"#ca9161",
                    'Q5Reputation History Sceptical':"#ca9161",
                    'Q5c':"#f0f0f0",#8, grey colorblind
                    'Q5Capitalist':"#f0f0f0",
                    'Q5b':"#ffd92f",#9, yellow colorblind
                    'Q5Benchmark':"#ffd92f",
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
                    'QDhs':"#e8000b",
                    'QDRep. Hist. Sceptical':"#e8000b",
                    'QDReputation History Sceptical':"#e8000b",
                    'QDc':"#e8000b",
                    'QDCapitalist':"#e8000b",
                    'QDb':"#e8000b",
                    'QDBenchmark':"#e8000b",
                    #newcomers:
                    # 'NEWn':"#a3a3a3",# grey
                    # 'NEWNaive':"#a3a3a3",
                    # 'NEWs':"#a3a3a3",
                    # 'NEWSceptical':"#a3a3a3",
                    # 'NEWr':"#a3a3a3",
                    # 'NEWRep. Ranking':"#a3a3a3",
                    # 'NEWReputation Ranking':"#a3a3a3",
                    # 'NEWNv':"#a3a3a3",
                    # 'NEWVariable Sc.':"#a3a3a3",
                    # 'NEWVariable Scepticism':"#a3a3a3",
                    # 'NEWt':"#a3a3a3",
                    # 'NEWRep. Threshold':"#a3a3a3",
                    # 'NEWReputation Threshold':"#a3a3a3",
                    # 'NEWh':"#a3a3a3",
                    # 'NEWRep. History':"#a3a3a3",
                    # 'NEWReputation History':"#a3a3a3",
                    # 'NEWhs':"#a3a3a3",
                    # 'NEWRep. Hist. Sceptical':"#a3a3a3",
                    # 'NEWReputation History Sceptical':"#a3a3a3",
                    }
NOISE_GROUPS_PALETTE = {
                    'ALL':"#0173b2",#, blue colorblind
                    'all':"#0173b2",
                    'A':"#0173b2",
                    'a':"#0173b2",
                    'GOOD':"#029e73",#, green colorblind
                    'good':"#029e73",
                    'G':"#029e73",
                    'g':"#029e73",
                    'BAD':"#de8f05",#orange colorblind
                    'bad':"#de8f05",
                    'B':"#de8f05",
                    'b':"#de8f05",
                    'SABOTEUR':"#e8000b",# bright red
                    'saboteur':"#e8000b",
                    'S':"#e8000b",
                    's':"#e8000b",
}
MARKET_CAP_COLOR="#000000"#black
BEHAV_PARAMS_COMBINATIONS={"n":[[]],
                                "s":[[0.25]],
                                "b":[
                                    [.75,.25,0],
                                    [.75,.25,.075],
                                    [.75,.25,.15],
                                    [.75,.4,0],
                                    [.75,.4,.075],
                                    [.75,.4,.15],
                                    [.75,.55,0],
                                    [.75,.55,.075],
                                    [.75,.55,.15],
                                    [.85,.25,0],
                                    [.85,.25,.075],
                                    [.85,.25,.15],
                                    [.85,.4,0],
                                    [.85,.4,.075],
                                    [.85,.4,.15],
                                    [.85,.55,0],
                                    [.85,.55,.075],
                                    [.85,.55,.15],
                                    [.95,.25,0],
                                    [.95,.25,.075],
                                    [.95,.25,.15],
                                    [.95,.4,0],
                                    [.95,.4,.075],
                                    [.95,.4,.15],
                                    [.95,.55,0],
                                    [.95,.55,.075],
                                    [.95,.55,.15],
                                    ],
                                "r":[
                                    [0.3,"r"],
                                    # [0.5,"r"],
                                    [0.3,"t"],
                                    # [0.5,"t"],
                                    ],
                                "Nv":[
                                    ["allavg",0.3,0.25,"ratio"],
                                    ["allavg",0.5,0.25,"ratio"],
                                    # ["allavg",0.3,0.25,"exponential"],
                                    # ["allavg",0.5,0.25,"exponential"],
                                    # ["allavg",0.8,0.25,"exponential"],
                                    # ["allavg",0.8,0.25,"ratio"],
                                    # ["allmax",0.3,0.25,"exponential"],
                                    # ["allmax",0.5,0.25,"exponential"],
                                    # ["allmax",0.8,0.25,"exponential"],
                                    # ["allmax",0.3,0.25,"ratio"],
                                    # ["allmax",0.5,0.25,"ratio"],
                                    # ["allmax",0.8,0.25,"ratio"]
                                    ],
                                "t":[
                                    ["allavg",0.5,"r"],
                                    # ["allavg",0.8,"r"],
                                    # ["allavg",0.5,"t"],
                                    # ["allavg",0.8,"t"],
                                    # ["allavg",0.3],
                                    # ["allmax",0.3],
                                    # ["allmax",0.5],
                                    # ["allmax",0.8]
                                    ],
                                "w":[[]],
                                "h":[
                                    ["discrete","mean",1,1],
                                    ["difference","mean",1,1],
                                    # ["discrete","mean",0.8,1],
                                    # ["difference","mean",0.8,1],
                                    # ["aged","mean",0.8,1],
                                    # ["aged2","mean",0.8,1.3],
                                    # ["recency","mean",1,1],
                                    # ["aged","mean",1,1],
                                    # ["aged2","mean",1,1],
                                    ],
                                    "hs":[
                                    ["discrete","mean",1,1,0.25],
                                    ["difference","mean",1,1,0.25],
                                    # ["discrete","mean",0.8,1,0.25],
                                    # ["difference","mean",0.8,1,0.25],
                                    # ["aged","mean",1,1,0.25],
                                    # ["aged","mean",1,1.3,0.25],
                                    # ["aged","mean",0.8,1,0.25],
                                    # ["aged","mean",0.8,1.3,0.25],
                                    # ["discrete","mean",1,1.3,0.25],
                                    # ["discrete","mean",0.8,1.3,0.25],
                                    # ["difference","mean",1,1.3,0.25],
                                    # ["difference","mean",0.8,1.3,0.25],
                                    ],
                                    "c":[
                                        ["r"],
                                        ["t"],
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


def dataframe_from_csv(
                        filename,
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

    # if data_folder_and_subfolder!="" and metric!="":filename=join(data_folder_and_subfolder,metric,filename)
    #NOTE "lastN": ONLY items allowed (always monotonic non decreasing)
    if experiment_part=="whole" or "transaction" in metric \
            or (('reward' in filename.split('/')[-2] or  'wealth' in filename.split('/')[-2]) \
            and 'df' not in experiment_part \
            and 'steps' not in experiment_part):#NOTE BYPASS NEGATIVE REWARD ISSUE
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
        if data_folder_and_subfolder=="":
            df=pd.read_csv(filename, header=None)
        else:
            df=pd.read_csv(join(data_folder_and_subfolder,filename), header=None)

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

    elif "steps" in experiment_part or "df" in experiment_part:
        def string_list_to_array(string:str, element_type=int):
            return np.asarray([element_type(_) for _ in string.replace("[","").replace("]","").split(", ")])
        if "item" in metric: metric_folder="items_evolution"
        elif "reward" in metric: metric_folder="rewards_evolution"
        elif "wealth" in metric: metric_folder="wealth_evolution"

        if data_folder_and_subfolder!="" and metric!="":filename=join(data_folder_and_subfolder,metric_folder,filename)

        df=pd.read_csv(filename)

        col_labels=df.columns.to_list()
        df_list=[]
        for _,row in df.iterrows():
            row_list=string_list_to_array(row[col_labels[-1]],element_type=int if "item" in metric else float)
            new_row=[row[col_labels[0]],row[col_labels[1]],*row_list]
            df_list.append(new_row if "df" in experiment_part else new_row[2:])
        existing_labels=col_labels[:-1] if "df" in experiment_part else []
        new_col_labels=existing_labels+[f"{metric}_{robot_id}" for robot_id in range(len(row_list))]
        # if "df" in experiment_part:df=pd.DataFrame(df_list,columns=new_col_labels)
        # else: df=df_list
        df=pd.DataFrame(df_list,columns=new_col_labels)

    if not noise_group=="all" and noise_group!="" and noise_group is not None:
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

    if post_processing is not None and post_processing!="":
        #NOTE RETURN TYPE: pandas.Series
        FUN_DICT={"sum":np.sum,"mean":np.mean,"std":np.std,"median":np.median,"min":np.min,"max":np.max}
        items,function=post_processing.split("-")
        if 'df' in experiment_part:
            df_not_to_consider,df=df.iloc[:,:2],df.iloc[:,2:]
        if items=="row" or "exp" in items: axis=1
        elif items=="col" or "rob" in items: axis=0
        elif items=="all" or items=="both":
            df=df.apply(FUN_DICT[function],axis=0)
            df=FUN_DICT[function](df)
            df=pd.Series(df)
            if 'df' in experiment_part:
                df=pd.concat([df_not_to_consider,df],axis=1)
                df.columns=df.columns[:-1].to_list()+[metric_folder+"_"+function]
            return df
        df=df.apply(FUN_DICT[function],axis=axis)
    return df


#TODO rework best, worst run seeds
def find_best_worst_seeds(filenames=[],
                        metric="",
                        data_folder="",
                        base_seed="",
                        amount_to_find=1):
    """
    returns the AMOUNT_TO_FIND best and worst seeds, wrt given metric.
    result computed assuminig a linear increare with the run number,
    starting from BASE_SEED

    if metric="" and data_folder="", filename in filenames is expected
    in this shape /DATA_DIR/METRIC/FILENAME.csv
    """
    if amount_to_find<1:amount_to_find=1
    data_folder=join(data_folder,metric) if data_folder!="" else ""
    if not filenames:
        filenames.extend([join(data_folder, f)
            for f in os.listdir(data_folder) if isfile(join(data_folder, f))])
    else:
        filenames=[f"{data_folder}{f}" for f in filenames]

    for filename in filenames:
        bests=[]
        worsts=[]
        df=pd.read_csv(filename,header=None)
        df['items_sum']=df.apply(np.sum, axis=1)
        average_sum=df["items_sum"].mean()

        print(f"\nfile: {filename.split('/')[-1]}")
        print(f"average sum: {average_sum} over {len(df)} runs")

        for i in range(amount_to_find):
            i_max=df["items_sum"].max()
            i_id_max=df["items_sum"].idxmax()
            i_min=df["items_sum"].min()
            i_id_min=df["items_sum"].idxmin()
            bests.append((base_seed+i_id_max, i_max))
            worsts.append((base_seed+i_id_min, i_min))
            df.drop(i_id_max, inplace=True)
            df.drop(i_id_min, inplace=True)

        for i, best in enumerate(bests):
            print(f"{1+i} best seed: {best[0]} (run {best[0]-base_seed}), value: {best[1]}")
        for i, worst in enumerate(worsts):
            print(f"{1+i} worst seed: {worst[0]} (run {worst[0]-base_seed}), value: {worst[1]}")


#TODO t test informative for multiple experiments
def myttest(
            filenames=[],
            data_folder="../data/",\
            compare="scaboteur_rotation",\
            # metric="rewards",
            metric="items_collected",
            ):
    '''
    :param filenames: list of filenames to compare,
                    NOTE: ONLY FIRST TWO FILES ARE COMPARED
    '''
    filenames = [
            "24sceptical_025th_1scaboteur_0rotation_nopenalisation.txt",
            "24sceptical_025th_1scaboteur_0rotation_nopenalisation.txt"
            ]
    data1=pd.read_csv(f"{data_folder}{compare+'/' if compare!='' else ''}{metric}/{filenames[0]}").apply(np.sum, axis=1)
    data2=pd.read_csv(f"{data_folder}{compare+'/' if compare!='' else ''}{metric}/{filenames[1]}").apply(np.sum, axis=1)
    print(type(pd.read_csv(f"{data_folder}{compare+'/' if compare!='' else ''}{metric}/{filenames[1]}")))
    t_test=stats.ttest_ind(data1, data2, equal_var=False)
    print(f"t-test: {t_test.statistic},\n p-value: {t_test.pvalue}")


#TODO anova test informative for multiple experiments
def myanovatest(
                filenames=[],
                data_folder="../data/",\
                compare="scaboteur_rotation",\
                metric="items_collected",
                ):
    filenames = [
            ]
    data1=pd.read_csv(f"{data_folder}{compare}/{metric}/{filenames[0]}").apply(np.sum, axis=1)
    data2=pd.read_csv(f"{data_folder}{compare}/{metric}/{filenames[1]}").apply(np.sum, axis=1)
    anova_test=stats.f_oneway(data1, data2)
    print(f"F-statistic: {anova_test.statistic},\np-value: {anova_test.pvalue}\n")


#######################################################################################################################
#######################################################################################################################
########################################## BASE PLOTTING FUNCTIONS ####################################################
def noise_level(
#TODO noise levels colored for each noise group
            number_agents=25,
            number_saboteurs=3,
            noise_average=0.05,
            noise_range=0.05,
            saboteurs_noise="",
            equally_sized_honest_groups=False,
            random_switch=False,
            random_seed=None
        ):
    '''
    TODO noise_level docstring
    :param saboteurs_noise: noise performance. Accepted: "bimodal", "average", "perfect".

    :param equally_sized_honest_groups: if True, the honest robots are divided in
            equally sized groups even for perfect saboteurs (as in the average sab. case).
    '''
    noise_list=generate_uniform_noise_list(number_agents, number_saboteurs, saboteurs_noise,
                                         noise_average, noise_range,random_switch,random_seed)
    fig, ax = plt.subplots()
    fig.set_size_inches(8,8)
    barlist=plt.bar(range(len(noise_list)), noise_list)
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
    [bar.set_color(NOISE_GROUPS_PALETTE['S']) for bar in barlist[number_agents-number_saboteurs:number_agents]]
    plt.show()
    # plt.pause(0.001)


def plot_variable_stake():
    def reputation_stake(saturate=True):
        def reputation_stake_coeff(reputation,saturate=True):
            stake_ratio_min=0.5
            history_span=10
            if reputation<0 or not saturate:
                stake_ratio=stake_ratio_min**(2*reputation/history_span)
            else:
                stake_ratio=1
            return stake_ratio
        base_stake_amount=0.04
        reputation_vector=np.linspace(-10,10,21)
        stake_vector=[base_stake_amount*reputation_stake_coeff(reputation,saturate) for reputation in reputation_vector]
        return reputation_vector,stake_vector
    #plot reputation_vector vs stake_vector for both saturate=True and False, in a single plot
    reputation_vector,saturated_stake_vector=reputation_stake()
    _,unsaturated_stake_vector=reputation_stake(saturate=False)
    fig, ax = plt.subplots()
    fig.set_size_inches(8,8)
    #plot dotted line at constant base_stake_amount
    plt.plot(reputation_vector,[0.04 for _ in reputation_vector],linestyle='dashed',label="base stake amount")
    plt.plot(reputation_vector,saturated_stake_vector,label="punishing negative reputation",linewidth=3)
    plt.plot(reputation_vector,unsaturated_stake_vector,label="rewarding positive reputation")
    plt.xlabel("reputation")
    plt.ylabel("stake amount")
    plt.yticks(np.arange(0.01, 0.17,0.03))
    plt.xticks(np.arange(-10, 11, 1))
    #rotate x ticks
    plt.xticks(rotation=45)
    #change colors
    plt.gca().lines[0].set_color('grey')
    plt.gca().lines[2].set_color('orange')
    plt.gca().lines[1].set_color('blue')

    plt.legend()
    plt.show()



def noise_metric_analysis(
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
                        save_name="noise_vs_metric",
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
                        quality_index="transactionsS",#"reward"
                        equally_sized_honest_groups=False,
                        pair_plot=False,
                        multi_quality=True,
                        title="",
                        x_labels=[],
                        show_dishonests=True,
                        transparent_boxes=False,
                        multi_plot=False,
                        save_plot=False,
                        save_folder="",
                        save_name="performance_with_quality",
                    ):
    '''
    TODO performance_with_quality docstring
    This method prints a sequence of given boxplots, each one representing a different behaviour.
    On the left y axis, the value of the performance is represented.
    Additionally, on the right y axis, the value of the quality index is represented.

    :param filenames: list of filenames to be plotted. Required format: [filename1, filename2, ...]

    :param performance_index: the performance index to be plotted. As for now, only "items" is supported.

    :param equally_sized_honest_groups: if True, the honest robots are divided in
            equally sized groups even for perfect saboteurs (as in the average sab. case).

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
            n_honest, honest_behavior, _, payment,reputation_stake, _, \
                    behaviour_params, noise_params=params_from_filename(f,compact_format=True)
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

                        good_slice,bad_slice=noise_groups_slices(n_robots,n_dishonest,
                                            saboteur_performance if not equally_sized_honest_groups else "bypass")
                        #TODO narrower good/bad groups
                        #NOTE pandas.Series, hence can slice with iloc[a:b] groupwise
                        df_q_good_num=df_q_num.iloc[:good_slice]#-narrow_slice]
                        df_q_good_den=df_q_den.iloc[:good_slice]#-narrow_slice]
                        df_q_bad_num=df_q_num.iloc[good_slice:bad_slice]#-narrow_slice:bad_slice+narrow_slice]
                        df_q_bad_den=df_q_den.iloc[good_slice:bad_slice]#-narrow_slice:bad_slice+narrow_slice]
                        df_q_good=100*df_q_good_num/df_q_good_den
                        df_q_bad=100*df_q_bad_num/df_q_bad_den
                        df_q_good=pd.Series(np.mean(df_q_good))
                        df_q_bad=pd.Series(np.mean(df_q_bad))

                        if n_dishonest>0:
                            df_q_dishonest_num=df_q_num.iloc[n_honest:]
                            df_q_dishonest_den=df_q_den.iloc[n_honest:]
                            df_q_dishonest=100*df_q_dishonest_num/df_q_dishonest_den
                            df_q_dishonest=pd.Series(np.mean(df_q_dishonest))
                            df_quality=np.sum(df_q_good_den)/np.sum(df_q_den)*df_q_good+ \
                                        np.sum(df_q_bad_den)/np.sum(df_q_den)*df_q_bad + \
                                        np.sum(df_q_dishonest_den)/np.sum(df_q_den) * df_q_dishonest
                        else:
                            pass
                            df_quality=np.sum(df_q_good_num)/np.sum(df_q_num)*df_q_good+ \
                                np.sum(df_q_bad_num)/np.sum(df_q_num)*df_q_bad
                    else:
                        df_quality=100*df_q_num/df_q_den

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
                    #NOTE following case: use single boxplot for median+specific quality
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
                            linewidth=3 if transparent_boxes else 1, dodge=False,width=.5,ax=axs[j])#
            # sns.boxplot(data=pd.melt(data_small, id_vars=['behavior','plot_order']),
            #                 x='plot_order',y='value', hue='behavior',palette=BEHAVIOUR_PALETTE,
            #                 linewidth=1.65, dodge=True, saturation=0.85, width=0.7, ax=axs[j])
            sns.boxplot(data=pd.melt(data_dishonest, id_vars=['behavior','plot_order']),
                            x='plot_order',y='value', hue='behavior',palette=BEHAVIOUR_PALETTE,
                            linewidth=4.65 if transparent_boxes else 1.65, dodge=True, saturation=0.85, width=0.5, ax=axs[j])

            #BUG same size paired boxplots label not aligned
            # data_full=pd.concat([data_honest,data_dishonest])
            # sns.boxplot(data=pd.melt(data_full, id_vars=['behavior','plot_order']),
            #                 x='plot_order',y='value', hue='behavior',palette=BEHAVIOUR_PALETTE,
            #                 linewidth=1, dodge=True,width=2.5)
        else:
            data_performance=pd.concat(performance_list)
            sns.boxplot(data=pd.melt(data_performance, id_vars=['behavior','plot_order']),
                            x='plot_order',y='value', hue='behavior',palette=BEHAVIOUR_PALETTE,
                            linewidth=3 if transparent_boxes else 1, dodge=False,width=.5,ax=axs[j])
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
            
            if transparent_boxes:
                
                box_patches = [patch for patch in axs[j].patches if type(patch) == matplotlib.patches.PathPatch]# type: ignore # pylint: disable=import-error
                if len(box_patches) == 0:  #matplotlib<3.5: boxes in ax.artists
                    box_patches = axs[j].artists
                num_patches = len(box_patches)
                lines_per_boxplot = len(axs[j].lines) // num_patches
                for i, patch in enumerate(box_patches):
                    col = patch.get_facecolor()
                    patch.set_edgecolor(col)
                    # patch.set_facecolor('black')
                    patch.set_facecolor('None')
                    #whiskers
                    for line in axs[j].lines[i * lines_per_boxplot: (i + 1) * lines_per_boxplot]:
                        line.set_color(col)
                        line.set_mfc(col)
                        line.set_mec(col)
                    #legend
                    # for legpatch in axs[j].legend_.get_patches():
                    #     col = legpatch.get_facecolor()
                    #     legpatch.set_edgecolor(col)
                    #     legpatch.set_facecolor('None')

            if j>0 or not pair_plot:
                ax2=axs[j].twinx()
                if 'trans' in quality_index:
                    ax2.yaxis.set_major_formatter(mtick.PercentFormatter())

                if not pair_plot or j>0:
                    sns.pointplot(data=pd.melt(data_quality,id_vars=['behavior','plot_order']),palette=BEHAVIOUR_PALETTE,
                                    x='plot_order',y='value', hue='behavior',
                                    markers="o",
                                    # markers=["*","+","o","."]*5,
                                    ax=ax2,join=False,errorbar=None)
                    if multi_quality:
                        #matplotlib markers https://matplotlib.org/3.1.0/api/markers_api.html
                        sns.pointplot(data=pd.melt(data_quality_good,id_vars=['behavior','plot_order']),palette=BEHAVIOUR_PALETTE,
                                        x='plot_order',y='value', hue='behavior',ax=ax2,markers="^",scale=0.85,join=False,errorbar=None)

                        sns.pointplot(data=pd.melt(data_quality_bad,id_vars=['behavior','plot_order']),palette=BEHAVIOUR_PALETTE,
                                        x='plot_order',y='value', hue='behavior',ax=ax2,markers="s",scale=0.85,join=False,errorbar=None)
                        if n_dishonest>0:
                            warnings.filterwarnings( "ignore", module = "seaborn\..*" )#ignore color of "x" warning
                            sns.pointplot(data=pd.melt(data_quality_dishonest,id_vars=['behavior','plot_order']),palette=BEHAVIOUR_PALETTE,
                                            x='plot_order',y='value', hue='behavior',ax=ax2,markers="x",scale=0.85,join=False,errorbar=None)
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
        # plt.ylim(-1 if 'item' in performance_label else None,
        #                 35 if 'item' in performance_label and experiment_part=='whole' else \
        #                 14 if 'item' in performance_label and 'last' in experiment_part \
        #                     else None)#int(1.25*performance_max))
        if not pair_plot and quality_index!="":
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


def market_metric_evolution(
                        filename:str,
                        data_folder_and_subfolder:str="",
                        metric:str="reward_evolution",
                        number_of_robots:int=25,
                        equally_sized_honest_groups=False,
                        multi_plot:bool=False,
                        pair_plot:bool=False,
                        fill_between:bool=False,
                        individual_group_sum:bool=True,
                        save_plot:bool=False,
                        save_folder:str="",
                        save_name:str="",
                    ):
    '''
    TODO market_metric_evolution docstring
    :param equally_sized_honest_groups: if True, the honest robots are divided in
            equally sized groups even for perfect saboteurs (as in the average sab. case).
    '''
    line_width=1
    if 'reward' in metric:
        metric="rewards_evolution"
    elif 'wealth' in metric:
        metric="wealth_evolution"

    params=params_from_filename(filename,compact_format=True)
    title_params=params_from_filename(filename)
    title=f"{title_params[0]}honest {BEHAVIORS_NAME_DICT[params[1]]},{title_params[5]} lie angle,"\
    f"{'reputation' if params[4] and params[3]=='P' else ''} {'staking' if params[3]=='P' else 'no staking'}\n"\
    f"noise: {title_params[7]}\n behaviour params: {title_params[6]}".replace(",",", ")

    number_of_honest=int(params[0])
    number_of_saboteurs=number_of_robots-number_of_honest
    saboteur_performance=params[7][2]
    
    good_slice,bad_slice=noise_groups_slices(number_of_robots,number_of_saboteurs,
                                            saboteur_performance if not equally_sized_honest_groups else "bypass")
    df=dataframe_from_csv(join(data_folder_and_subfolder,metric,filename),
                                metric=metric,experiment_part="df")

    sim_col=df.columns.to_list()[0]
    tick_col=df.columns.to_list()[1]
    agent_col=df.columns.to_list()[2:]
    selected_runs=df[df.columns.to_list()[0]].unique()
    selected_ticks=df[df.columns.to_list()[1]].unique()

    df_reference_initial=pd.Series(7,index=selected_ticks)

    # for agent in range(len(agent_col)):#ALL
    #     sns.lineplot(data=pd.melt(df, id_vars=['tick']+agent_col),x=df.columns.to_list()[1],y=df.columns.to_list()[2+agent],errorbar=("sd"))
    # for agent in [0,1,2]:# BYZ
    #     sns.lineplot(data=pd.melt(df, id_vars=['tick']+agent_col),x=df.columns.to_list()[1],y=df.columns.to_list()[24-agent],errorbar=("sd",0.1))

    # for run in selected_runs:
    #     df_run=df[df[df.columns.to_list()[0]]==run]
    #     for agent in range(len(agent_col)):
    #         df_run_agent=df_run.iloc[:,2+agent]

    legend=["all","good","bad"]
    #MEAN VALUES
    df_allagents_tick_mean=df.groupby(['tick']).mean().drop(columns=sim_col)
    df_meanagents_tick_mean=df_allagents_tick_mean.mean(axis=1)
    df_allgood_tick_mean=df_allagents_tick_mean[agent_col[:good_slice]]
    df_allbad_tick_mean=df_allagents_tick_mean[agent_col[good_slice:bad_slice]]
    df_meangood_tick_mean=df_allgood_tick_mean.mean(axis=1)
    df_meanbad_tick_mean=df_allbad_tick_mean.mean(axis=1)
    # df_meangood_tick_mean.name="good"

    fig,axs=plt.subplots(1,4 if pair_plot else 2,figsize=(15,10))
    plt.subplots_adjust(bottom=0.075,top=0.88,right=0.98,left=0.05,wspace=None,hspace=None)
    axs[0].set_ylim(bottom=0,auto=True)
    if pair_plot:
        axs[2].set_ylim(bottom=0,auto=True)
        axs[1].sharey(axs[0])
        axs[3].sharey(axs[2])
    else:
        axs[1].set_ylim(bottom=0,auto=True)

    sns.lineplot(data=df_meanagents_tick_mean,ax=axs[0],errorbar=None,color=NOISE_GROUPS_PALETTE['all'],linewidth=line_width)
    sns.lineplot(data=df_meangood_tick_mean,ax=axs[0],errorbar=None,color=NOISE_GROUPS_PALETTE['good'],linewidth=line_width)
    sns.lineplot(data=df_meanbad_tick_mean,ax=axs[0],errorbar=None,color=NOISE_GROUPS_PALETTE['bad'],linewidth=line_width)
    if number_of_saboteurs>0:
        legend.append("saboteur")
        df_allsab_tick_mean=df_allagents_tick_mean[agent_col[bad_slice:]]
        df_meansab_tick_mean=df_allsab_tick_mean.mean(axis=1)
        sns.lineplot(data=df_meansab_tick_mean,ax=axs[0],errorbar=None,color=NOISE_GROUPS_PALETTE['saboteur'],linewidth=line_width)
    axs[0].set_title(f"{metric.replace('_',' ').replace('evolution','mean').upper()}")

    if pair_plot:
        if 'reward' in metric:
            secondary_metric="wealth_evolution"
        elif 'wealth' in metric:
            secondary_metric="rewards_evolution"

        df_secondary=dataframe_from_csv(join(data_folder_and_subfolder,secondary_metric,filename),
                                metric=secondary_metric,experiment_part="df")
        agent_col_secondary=df_secondary.columns.to_list()[2:]
        df_secondary_allagents_tick_mean=df_secondary.groupby(['tick']).mean().drop(columns=sim_col)
        df_secondary_meanagents_tick_mean=df_secondary_allagents_tick_mean.mean(axis=1)
        df_secondary_allgood_tick_mean=df_secondary_allagents_tick_mean[agent_col_secondary[:good_slice]]
        df_secondary_allbad_tick_mean=df_secondary_allagents_tick_mean[agent_col_secondary[good_slice:bad_slice]]
        df_secondary_meangood_tick_mean=df_secondary_allgood_tick_mean.mean(axis=1)
        df_secondary_meanbad_tick_mean=df_secondary_allbad_tick_mean.mean(axis=1)

        sns.lineplot(data=df_secondary_meanagents_tick_mean,ax=axs[1],errorbar=None,color=NOISE_GROUPS_PALETTE['all'],linewidth=line_width)
        sns.lineplot(data=df_secondary_meangood_tick_mean,ax=axs[1],errorbar=None,color=NOISE_GROUPS_PALETTE['good'],linewidth=line_width)
        sns.lineplot(data=df_secondary_meanbad_tick_mean,ax=axs[1],errorbar=None,color=NOISE_GROUPS_PALETTE['bad'],linewidth=line_width)
        if number_of_saboteurs>0:
            df_secondary_allsab_tick_mean=df_secondary_allagents_tick_mean[agent_col_secondary[bad_slice:]]
            df_secondary_meansab_tick_mean=df_secondary_allsab_tick_mean.mean(axis=1)
            sns.lineplot(data=df_secondary_meansab_tick_mean,ax=axs[1],errorbar=None,color=NOISE_GROUPS_PALETTE['saboteur'],linewidth=line_width)
        axs[1].set_title(f"{secondary_metric.replace('_',' ').replace('evolution','mean').upper()}")

    #SUM VALUES (MEAN, paired with it)
    #TODO change order: better to have [0]:metric mean,[1]:m.sum, [2]:second m.mean, [3]:second m.sum?
    sum_legend=(["market cap"] if individual_group_sum else [])+legend[1:]
    df_meanagent_tick_sum=df_allagents_tick_mean.sum(axis=1)
    df_meangood_tick_sum=df_allgood_tick_mean.sum(axis=1)
    df_meanbad_tick_sum=df_allbad_tick_mean.sum(axis=1)

    if individual_group_sum:
        sns.lineplot(data=df_meanagent_tick_sum,ax=axs[1] if not pair_plot else axs[2],errorbar=None,color=MARKET_CAP_COLOR,linewidth=line_width,)
        sns.lineplot(data=df_meangood_tick_sum,ax=axs[1] if not pair_plot else axs[2],errorbar=None,color=NOISE_GROUPS_PALETTE['good'],linewidth=line_width,linestyle='--')
        sns.lineplot(data=df_meanbad_tick_sum,ax=axs[1] if not pair_plot else axs[2],errorbar=None,color=NOISE_GROUPS_PALETTE['bad'],linewidth=line_width,linestyle='--')
    if number_of_saboteurs>0:
        df_meansab_tick_sum=df_allsab_tick_mean.sum(axis=1)
        if individual_group_sum:
            sns.lineplot(data=df_meansab_tick_sum,ax=axs[1] if not pair_plot else axs[2],errorbar=None,color=NOISE_GROUPS_PALETTE['saboteur'],linewidth=line_width,linestyle='--')
        if fill_between:
            (axs[1] if not pair_plot else axs[2]).fill_between(df_meanbad_tick_sum.index,0,df_meansab_tick_sum,color=NOISE_GROUPS_PALETTE['saboteur'],alpha=0.5)
            (axs[1] if not pair_plot else axs[2]).fill_between(df_meanbad_tick_sum.index,df_meansab_tick_sum,df_meansab_tick_sum+df_meanbad_tick_sum,color=NOISE_GROUPS_PALETTE['bad'],alpha=0.5)
            (axs[1] if not pair_plot else axs[2]).fill_between(df_meanbad_tick_sum.index,df_meansab_tick_sum+df_meanbad_tick_sum,df_meanagent_tick_sum,color=NOISE_GROUPS_PALETTE['good'],alpha=0.5)
    elif fill_between:
        (axs[1] if not pair_plot else axs[2]).fill_between(df_meanbad_tick_sum.index,0,df_meanbad_tick_sum,color=NOISE_GROUPS_PALETTE['bad'],alpha=0.5)
        (axs[1] if not pair_plot else axs[2]).fill_between(df_meanbad_tick_sum.index,df_meanbad_tick_sum,df_meanagent_tick_sum,color=NOISE_GROUPS_PALETTE['good'],alpha=0.5)
    (axs[1] if not pair_plot else axs[2]).set_title(f"{metric.replace('_',' ').replace('evolution','sum').upper()}")

    if pair_plot:
        df_secondary_meanagent_tick_sum=df_secondary_allagents_tick_mean.sum(axis=1)
        df_secondary_meangood_tick_sum=df_secondary_allgood_tick_mean.sum(axis=1)
        df_secondary_meanbad_tick_sum=df_secondary_allbad_tick_mean.sum(axis=1)

        if individual_group_sum:
            sns.lineplot(data=df_secondary_meanagent_tick_sum,ax=axs[3],errorbar=None,color=MARKET_CAP_COLOR,linewidth=line_width,)
            sns.lineplot(data=df_secondary_meangood_tick_sum,ax=axs[3],errorbar=None,color=NOISE_GROUPS_PALETTE['good'],linewidth=line_width,linestyle='--')
            sns.lineplot(data=df_secondary_meanbad_tick_sum,ax=axs[3],errorbar=None,color=NOISE_GROUPS_PALETTE['bad'],linewidth=line_width,linestyle='--')
        if number_of_saboteurs>0:
            df_secondary_meansab_tick_sum=df_secondary_allsab_tick_mean.sum(axis=1)
            if individual_group_sum:
                sns.lineplot(data=df_secondary_meansab_tick_sum,ax=axs[3],errorbar=None,color=NOISE_GROUPS_PALETTE['saboteur'],linewidth=line_width,linestyle='--')
            if fill_between:
                axs[3].fill_between(df_secondary_meanbad_tick_sum.index,0,df_secondary_meansab_tick_sum,color=NOISE_GROUPS_PALETTE['saboteur'],alpha=0.5)
                axs[3].fill_between(df_secondary_meanbad_tick_sum.index,df_secondary_meansab_tick_sum,df_secondary_meansab_tick_sum+df_secondary_meanbad_tick_sum,color=NOISE_GROUPS_PALETTE['bad'],alpha=0.5)
                axs[3].fill_between(df_secondary_meanbad_tick_sum.index,df_secondary_meansab_tick_sum+df_secondary_meanbad_tick_sum,df_secondary_meanagent_tick_sum,color=NOISE_GROUPS_PALETTE['good'],alpha=0.5)
        elif fill_between:
            axs[3].fill_between(df_secondary_meanbad_tick_sum.index,0,df_secondary_meanbad_tick_sum,color=NOISE_GROUPS_PALETTE['bad'],alpha=0.5)
            axs[3].fill_between(df_secondary_meanbad_tick_sum.index,df_secondary_meanbad_tick_sum,df_secondary_meanagent_tick_sum,color=NOISE_GROUPS_PALETTE['good'],alpha=0.5)
        axs[3].set_title(f"{secondary_metric.replace('_',' ').replace('evolution','sum').upper()}")
        axs[1].legend(legend,title="agent (noise) group")
    else:
        axs[0].legend(legend,title="agent (noise) group")
    axs[-1].legend(sum_legend,title="agent (noise) group")
    plt.suptitle(title,fontweight='bold')
    if save_plot:
        plt.savefig(f"{save_folder}/{save_name}_mean_sum.png")
        plt.close()

    fig,axs=plt.subplots(2 if pair_plot else 1,3,figsize=(15,10))#SECOND IMAGE
    # plt.subplots_adjust(bottom=0.1,top=0.90,right=0.98,left=0.025,wspace=None,hspace=None)
    plt.subplots_adjust(bottom=0.075,top=0.88,right=0.98,left=0.05,wspace=None,hspace=None)
    #EXTREMA VALUES
    df_allagents_tick_max=df.groupby(['tick']).max().drop(columns=sim_col)
    df_allgood_tick_max=df_allagents_tick_max[agent_col[:good_slice]]
    df_allbad_tick_max=df_allagents_tick_max[agent_col[good_slice:bad_slice]]
    df_meangood_tick_max=df_allgood_tick_max.mean(axis=1)
    df_meanbad_tick_max=df_allbad_tick_max.mean(axis=1)
    df_maxgood_tick_max=df_allgood_tick_max.max(axis=1)
    df_maxbad_tick_max=df_allbad_tick_max.max(axis=1)
    df_allagents_tick_min=df.groupby(['tick']).min().drop(columns=sim_col)
    df_allgood_tick_min=df_allagents_tick_min[agent_col[:good_slice]]
    df_allbad_tick_min=df_allagents_tick_min[agent_col[good_slice:bad_slice]]
    df_meangood_tick_min=df_allgood_tick_min.mean(axis=1)
    df_meanbad_tick_min=df_allbad_tick_min.mean(axis=1)
    df_mingood_tick_min=df_allgood_tick_min.min(axis=1)
    df_minbad_tick_min=df_allbad_tick_min.min(axis=1)
    legend_max=['mean good','mean bad','abs good','abs bad']
    legend_max=['initial']+legend_max
    legend_min=['mean good','mean bad','abs good','abs bad']
    # legend_min=['initial val.']+legend_min
    if number_of_saboteurs>0:
        df_allsab_tick_max=df_allagents_tick_max[agent_col[bad_slice:]]
        df_meansab_tick_max=df_allsab_tick_max.mean(axis=1)
        df_maxsab_tick_max=df_allsab_tick_max.max(axis=1)
        df_allsab_tick_min=df_allagents_tick_min[agent_col[bad_slice:]]
        df_meansab_tick_min=df_allsab_tick_min.mean(axis=1)
        df_minsab_tick_min=df_allsab_tick_min.min(axis=1)
        legend_max+=['mean byz','abs byz']
        legend_min+=['mean byz','abs byz']

    sns.lineplot(data=df_reference_initial,ax=axs[0][0] if pair_plot else axs[0],errorbar=None,color=MARKET_CAP_COLOR,linewidth=line_width,linestyle=':')
    sns.lineplot(data=df_meangood_tick_max,ax=axs[0][0] if pair_plot else axs[0],errorbar=None,color=NOISE_GROUPS_PALETTE['good'],linewidth=line_width)
    sns.lineplot(data=df_meanbad_tick_max,ax=axs[0][0] if pair_plot else axs[0],errorbar=None,color=NOISE_GROUPS_PALETTE['bad'],linewidth=line_width)
    sns.lineplot(data=df_maxgood_tick_max,ax=axs[0][0] if pair_plot else axs[0],errorbar=None,color=NOISE_GROUPS_PALETTE['good'],linewidth=line_width,linestyle='--')
    sns.lineplot(data=df_maxbad_tick_max,ax=axs[0][0] if pair_plot else axs[0],errorbar=None,color=NOISE_GROUPS_PALETTE['bad'],linewidth=line_width,linestyle='--')
    if number_of_saboteurs>0:
        sns.lineplot(data=df_meansab_tick_max,ax=axs[0][0] if pair_plot else axs[0],errorbar=None,color=NOISE_GROUPS_PALETTE['saboteur'],linewidth=line_width)
        sns.lineplot(data=df_maxsab_tick_max,ax=axs[0][0] if pair_plot else axs[0],errorbar=None,color=NOISE_GROUPS_PALETTE['saboteur'],linewidth=line_width,linestyle='--')

    if pair_plot:
        df_secondary_allagents_tick_max=df_secondary.groupby(['tick']).max().drop(columns=sim_col)
        df_secondary_allgood_tick_max=df_secondary_allagents_tick_max[agent_col_secondary[:good_slice]]
        df_secondary_allbad_tick_max=df_secondary_allagents_tick_max[agent_col_secondary[good_slice:bad_slice]]
        df_secondary_meangood_tick_max=df_secondary_allgood_tick_max.mean(axis=1)
        df_secondary_meanbad_tick_max=df_secondary_allbad_tick_max.mean(axis=1)
        df_secondary_maxgood_tick_max=df_secondary_allgood_tick_max.max(axis=1)
        df_secondary_maxbad_tick_max=df_secondary_allbad_tick_max.max(axis=1)
        df_secondary_allagents_tick_min=df_secondary.groupby(['tick']).min().drop(columns=sim_col)
        df_secondary_allgood_tick_min=df_secondary_allagents_tick_min[agent_col_secondary[:good_slice]]
        df_secondary_allbad_tick_min=df_secondary_allagents_tick_min[agent_col_secondary[good_slice:bad_slice]]
        df_secondary_meangood_tick_min=df_secondary_allgood_tick_min.mean(axis=1)
        df_secondary_meanbad_tick_min=df_secondary_allbad_tick_min.mean(axis=1)
        df_secondary_mingood_tick_min=df_secondary_allgood_tick_min.min(axis=1)
        df_secondary_minbad_tick_min=df_secondary_allbad_tick_min.min(axis=1)
        if number_of_saboteurs>0:
            df_secondary_allsab_tick_max=df_secondary_allagents_tick_max[agent_col_secondary[bad_slice:]]
            df_secondary_meansab_tick_max=df_secondary_allsab_tick_max.mean(axis=1)
            df_secondary_maxsab_tick_max=df_secondary_allsab_tick_max.max(axis=1)
            df_secondary_allsab_tick_min=df_secondary_allagents_tick_min[agent_col_secondary[bad_slice:]]
            df_secondary_meansab_tick_min=df_secondary_allsab_tick_min.mean(axis=1)
            df_secondary_minsab_tick_min=df_secondary_allsab_tick_min.min(axis=1)

        sns.lineplot(data=df_reference_initial,ax=axs[1][0],errorbar=None,color=MARKET_CAP_COLOR,linewidth=line_width,linestyle=':')
        sns.lineplot(data=df_secondary_meangood_tick_max,ax=axs[1][0],errorbar=None,color=NOISE_GROUPS_PALETTE['good'],linewidth=line_width)
        sns.lineplot(data=df_secondary_meanbad_tick_max,ax=axs[1][0],errorbar=None,color=NOISE_GROUPS_PALETTE['bad'],linewidth=line_width)
        sns.lineplot(data=df_secondary_maxgood_tick_max,ax=axs[1][0],errorbar=None,color=NOISE_GROUPS_PALETTE['good'],linewidth=line_width,linestyle='--')
        sns.lineplot(data=df_secondary_maxbad_tick_max,ax=axs[1][0],errorbar=None,color=NOISE_GROUPS_PALETTE['bad'],linewidth=line_width,linestyle='--')
        if number_of_saboteurs>0:
            sns.lineplot(data=df_secondary_meansab_tick_max,ax=axs[1][0],errorbar=None,color=NOISE_GROUPS_PALETTE['saboteur'],linewidth=line_width)
            sns.lineplot(data=df_secondary_maxsab_tick_max,ax=axs[1][0],errorbar=None,color=NOISE_GROUPS_PALETTE['saboteur'],linewidth=line_width,linestyle='--')
        axs[0][0].set_title(f"max values: {metric.replace('_',' ')}")
        axs[0][0].set_xlabel(None)
        axs[1][0].set_title(f"max values: {secondary_metric.replace('_',' ')}")
        axs[1][0].legend(legend_max,)
    else:
        axs[0].set_xlabel(None)
        axs[0].set_title(f"max values: {metric.replace('_',' ')}")
        axs[0].legend(legend_max,)

    sns.lineplot(data=df_meangood_tick_min,ax=axs[0][1] if pair_plot else axs[1],errorbar=None,color=NOISE_GROUPS_PALETTE['good'],linewidth=line_width)
    sns.lineplot(data=df_meanbad_tick_min,ax=axs[0][1] if pair_plot else axs[1],errorbar=None,color=NOISE_GROUPS_PALETTE['bad'],linewidth=line_width)
    sns.lineplot(data=df_mingood_tick_min,ax=axs[0][1] if pair_plot else axs[1],errorbar=None,color=NOISE_GROUPS_PALETTE['good'],linewidth=line_width,linestyle='--')
    sns.lineplot(data=df_minbad_tick_min,ax=axs[0][1] if pair_plot else axs[1],errorbar=None,color=NOISE_GROUPS_PALETTE['bad'],linewidth=line_width,linestyle='--')
    if number_of_saboteurs>0:
        sns.lineplot(data=df_meansab_tick_min,ax=axs[0][1] if pair_plot else axs[1],errorbar=None,color=NOISE_GROUPS_PALETTE['saboteur'],linewidth=line_width)
        sns.lineplot(data=df_minsab_tick_min,ax=axs[0][1] if pair_plot else axs[1],errorbar=None,color=NOISE_GROUPS_PALETTE['saboteur'],linewidth=line_width,linestyle='--')

    if pair_plot:
        sns.lineplot(data=df_secondary_meangood_tick_min,ax=axs[1][1],errorbar=None,color=NOISE_GROUPS_PALETTE['good'],linewidth=line_width)
        sns.lineplot(data=df_secondary_meanbad_tick_min,ax=axs[1][1],errorbar=None,color=NOISE_GROUPS_PALETTE['bad'],linewidth=line_width)
        sns.lineplot(data=df_secondary_mingood_tick_min,ax=axs[1][1],errorbar=None,color=NOISE_GROUPS_PALETTE['good'],linewidth=line_width,linestyle='--')
        sns.lineplot(data=df_secondary_minbad_tick_min,ax=axs[1][1],errorbar=None,color=NOISE_GROUPS_PALETTE['bad'],linewidth=line_width,linestyle='--')
        if number_of_saboteurs>0:
            sns.lineplot(data=df_secondary_meansab_tick_min,ax=axs[1][1],errorbar=None,color=NOISE_GROUPS_PALETTE['saboteur'],linewidth=line_width)
            sns.lineplot(data=df_secondary_minsab_tick_min,ax=axs[1][1],errorbar=None,color=NOISE_GROUPS_PALETTE['saboteur'],linewidth=line_width,linestyle='--')
        axs[0][1].set_title(f"min values: {metric.replace('_',' ')}")
        axs[0][1].set_xlabel(None)
        axs[1][1].set_title(f"min values: {secondary_metric.replace('_',' ')}")
        axs[1][1].legend(legend_min,)
        if not 'NODEFAULT' in data_folder_and_subfolder:
            axs[0][1].set_ylim(-0.1,1)
            axs[1][1].set_ylim(-0.1,4)
    else:
        axs[1].set_title(f"{params}\nmin values: {metric.replace('_',' ')}")
        axs[1].set_xlabel(None)
        axs[1].legend(legend_min,)
        if not 'NODEFAULT' in data_folder_and_subfolder: axs[1].set_ylim(-0.1,1)

    #VARIANCE/STANDARD DEVIATION
    # df_allagents_tick_var=df.groupby(['tick']).var().drop(columns=sim_col)
    df_allagents_tick_var=df.groupby(['tick']).std().drop(columns=sim_col)
    df_allgood_tick_var=df_allagents_tick_var[agent_col[:good_slice]]
    df_allbad_tick_var=df_allagents_tick_var[agent_col[good_slice:bad_slice]]
    df_meangood_tick_var=df_allgood_tick_var.mean(axis=1)
    df_meanbad_tick_var=df_allbad_tick_var.mean(axis=1)
    df_mingood_tick_var=df_allgood_tick_var.min(axis=1)
    df_minbad_tick_var=df_allbad_tick_var.min(axis=1)
    legend_var=['mean good','mean bad','min good','min bad',]
    if number_of_saboteurs>0:
        df_allsab_tick_var=df_allagents_tick_var[agent_col[bad_slice:]]
        df_meansab_tick_var=df_allsab_tick_var.mean(axis=1)
        df_minsab_tick_var=df_allsab_tick_var.min(axis=1)
        legend_var+=['mean byz','min byz', 'max byz']

    sns.lineplot(data=df_meangood_tick_var,ax=axs[0][2] if pair_plot else axs[2],errorbar=None,color=NOISE_GROUPS_PALETTE['good'],linewidth=line_width)
    sns.lineplot(data=df_meanbad_tick_var,ax=axs[0][2] if pair_plot else axs[2],errorbar=None,color=NOISE_GROUPS_PALETTE['bad'],linewidth=line_width)
    sns.lineplot(data=df_mingood_tick_var,ax=axs[0][2] if pair_plot else axs[2],errorbar=None,color=NOISE_GROUPS_PALETTE['good'],linewidth=line_width,linestyle='--')
    sns.lineplot(data=df_minbad_tick_var,ax=axs[0][2] if pair_plot else axs[2],errorbar=None,color=NOISE_GROUPS_PALETTE['bad'],linewidth=line_width,linestyle='--')
    if number_of_saboteurs>0:
        sns.lineplot(data=df_meansab_tick_var,ax=axs[0][2] if pair_plot else axs[2],errorbar=None,color=NOISE_GROUPS_PALETTE['saboteur'],linewidth=line_width)
        sns.lineplot(data=df_minsab_tick_var,ax=axs[0][2] if pair_plot else axs[2],errorbar=None,color=NOISE_GROUPS_PALETTE['saboteur'],linewidth=line_width,linestyle='--')

    if pair_plot:
        df_secondary_allagents_tick_var=df_secondary.groupby(['tick']).std().drop(columns=sim_col)
        # df_secondary_allagents_tick_var=df_secondary.groupby(['tick']).var().drop(columns=sim_col)
        df_secondary_allgood_tick_var=df_secondary_allagents_tick_var[agent_col_secondary[:good_slice]]
        df_secondary_allbad_tick_var=df_secondary_allagents_tick_var[agent_col_secondary[good_slice:bad_slice]]
        df_secondary_meangood_tick_var=df_secondary_allgood_tick_var.mean(axis=1)
        df_secondary_meanbad_tick_var=df_secondary_allbad_tick_var.mean(axis=1)
        df_secondary_mingood_tick_var=df_secondary_allgood_tick_var.min(axis=1)
        df_secondary_minbad_tick_var=df_secondary_allbad_tick_var.min(axis=1)
        if number_of_saboteurs>0:
            df_secondary_allsab_tick_var=df_secondary_allagents_tick_var[agent_col_secondary[bad_slice:]]
            df_secondary_meansab_tick_var=df_secondary_allsab_tick_var.mean(axis=1)
            df_secondary_minsab_tick_var=df_secondary_allsab_tick_var.min(axis=1)
        sns.lineplot(data=df_secondary_meangood_tick_var,ax=axs[1][2],errorbar=None,color=NOISE_GROUPS_PALETTE['good'],linewidth=line_width)
        sns.lineplot(data=df_secondary_meanbad_tick_var,ax=axs[1][2],errorbar=None,color=NOISE_GROUPS_PALETTE['bad'],linewidth=line_width)
        sns.lineplot(data=df_secondary_mingood_tick_var,ax=axs[1][2],errorbar=None,color=NOISE_GROUPS_PALETTE['good'],linewidth=line_width,linestyle='--')
        sns.lineplot(data=df_secondary_minbad_tick_var,ax=axs[1][2],errorbar=None,color=NOISE_GROUPS_PALETTE['bad'],linewidth=line_width,linestyle='--')
        if number_of_saboteurs>0:
            sns.lineplot(data=df_secondary_meansab_tick_var,ax=axs[1][2],errorbar=None,color=NOISE_GROUPS_PALETTE['saboteur'],linewidth=line_width)
            sns.lineplot(data=df_secondary_minsab_tick_var,ax=axs[1][2],errorbar=None,color=NOISE_GROUPS_PALETTE['saboteur'],linewidth=line_width,linestyle='--')
        axs[0][2].set_title(f"standard deviation values: {metric.replace('_',' ')}")
        # axs[0][2].set_title(f"variance values: {metric.replace('_',' ')}")
        axs[0][2].set_xlabel(None)
        axs[1][2].set_title(f"standard deviation values: {secondary_metric.replace('_',' ')}")
        # axs[1][2].set_title(f"variance values: {secondary_metric.replace('_',' ')}")
        axs[1][2].legend(legend_var,)
    else:
        axs[2].set_title(f"{params}\nstandard deviation values: {metric.replace('_',' ')}")
        # axs[2].set_title(f"{params}\nvariance values: {metric.replace('_',' ')}")
        axs[2].set_xlabel(None)
        axs[2].legend(legend_var,)
    plt.suptitle(title,fontweight="bold")

    if save_plot:
        plt.savefig(f"{save_folder}/{save_name}_std.png")
        plt.close()

    if not multi_plot and not save_plot:plt.show()


def performance_evolution(#[x]performance evolution
                        filename:str,
                        data_folder_and_subfolder:str="",
                        number_of_robots:int=25,
                        equally_sized_honest_groups=False,
                        window_size:int=5000,
                        metric:str='items_evolution',
                        multi_plot:bool=False,
                        pair_plot:bool=False,
                        # fill_between:bool=False,
                        save_plot:bool=False,
                        save_folder:str="",
                        save_name:str="",
                        ):
    '''
    TODO performance evolution docstring
    select a width of the sliding window and compute the evolution of performances in this interval
    :param equally_sized_honest_groups: if True, the honest robots are divided in
            equally sized groups even for perfect saboteurs (as in the average sab. case).
    '''
    print(filename)
    metric='items_evolution'

    params=params_from_filename(filename,compact_format=True)
    number_of_honest=int(params[0])
    number_of_saboteurs=number_of_robots-number_of_honest
    saboteur_performance=params[7][2]

    good_slice,bad_slice=noise_groups_slices(number_of_robots,number_of_saboteurs,
                                    saboteur_performance if not equally_sized_honest_groups else "bypass")

    title_params=params_from_filename(filename)
    title=f"{title_params[0]}honest {BEHAVIORS_NAME_DICT[params[1]]},{title_params[5]} lie angle,"\
    f"{'reputation' if params[4] and params[3]=='P' else ''} {'staking' if params[3]=='P' else 'no staking'}\n"\
    f"noise: {title_params[7]}\n behaviour params: {title_params[6]}".replace(",",", ")

    df_meanagents=dataframe_from_csv(join(data_folder_and_subfolder,metric,filename),
        metric=metric,experiment_part='df').groupby('tick').mean().drop(columns=['simulation_id'])
    selected_ticks=df_meanagents.index.unique().to_list()
    df_meanagents_delta=pd.DataFrame().reindex_like(df_meanagents.loc[window_size:])
    delta_ticks=selected_ticks[selected_ticks.index(window_size):]
    for tick in delta_ticks:
        val_min=df_meanagents.loc[tick-window_size]
        val_max=df_meanagents.loc[tick]
        df_meanagents_delta.loc[tick]=(val_max-val_min)
    df_meanagents_delta['mean']=df_meanagents_delta.mean(axis=1)
    df_meanagents_delta['good']=df_meanagents_delta.iloc[:,:good_slice].mean(axis=1)
    df_meanagents_delta['bad']=df_meanagents_delta.iloc[:,bad_slice:].mean(axis=1)
    if number_of_saboteurs>0:
        df_meanagents_delta['saboteur']=df_meanagents_delta.iloc[:,bad_slice:].mean(axis=1)

        
def market_wealth_distribution(
                            filename:str,
                            data_folder_and_subfolder:str="",
                            metric:str="wealth_evolution",
                            number_of_robots:int=25,
                            equally_sized_honest_groups=False,
                            weight_by_group_wealth:bool=0,
                            multi_plot:bool=False,
                            pair_plot:bool=False,
                            fill_between:bool=False,
                            save_plot:bool=False,
                            save_folder:str="",
                            save_name:str="",
                            ):
    '''
    #TODO instead of making quantiles or using full experiments, print stuff using:
          sns.distplot(data, bins=n_robots ,...) this will also interpolate 

    TODO market wealth distribution docstring
    devide the robots in groups of chosen percentile level and
    compute the wealth distribution for the percentiles

    :param equally_sized_honest_groups: if True, the honest robots are divided in
            equally sized groups even for perfect saboteurs (as in the average sab. case).
    '''

    # if 'reward' in metric:
    #     metric="rewards_evolution"
    # elif 'wealth' in metric:
    #     metric="wealth_evolution"
    metric="wealth_evolution"

    params=params_from_filename(filename,compact_format=True)
    number_of_honest=int(params[0])
    number_of_saboteurs=number_of_robots-number_of_honest

    title_params=params_from_filename(filename)
    title=f"{title_params[0]}honest {BEHAVIORS_NAME_DICT[params[1]]},{title_params[5]} lie angle,"\
    f"{'reputation' if params[4] and params[3]=='P' else ''} {'staking' if params[3]=='P' else 'no staking'}\n"\
    f"noise: {title_params[7]}\n behaviour params: {title_params[6]}".replace(",",", ")

    df=dataframe_from_csv(join(data_folder_and_subfolder,metric,filename),
                            metric=metric,experiment_part="df")
    selected_ticks=df[df.columns.to_list()[1]].unique()
    df_last=df[df['tick']==selected_ticks.max()].drop(columns=['tick','simulation_id'])

    df_last_allagents_sorted=pd.DataFrame(df_last.to_numpy().flatten()).sort_values(by=0,ascending=True).reset_index(drop=True)
    df_last_allagents_max=df_last_allagents_sorted.max().to_numpy()[0]
    df_last_allagents_min=df_last_allagents_sorted.min().to_numpy()[0]
    df_last_allagents_delta=df_last_allagents_max-df_last_allagents_min
    assigned_groups=[]
    for val in df_last_allagents_sorted[0]:#split in quantiles, wrt robot population
        assigned_groups.append(int((val-df_last_allagents_min)/df_last_allagents_delta*(number_of_robots-1)))
    df_last_allagents_sorted['quantile']=assigned_groups
    df_last_allagents_sorted['normalized_wealth']=df_last_allagents_sorted[0]/df_last_allagents_sorted.mean()[0]
    number_of_ranges=100
    normalized_wealth_max=df_last_allagents_sorted['normalized_wealth'].max()
    df_last_allagents_sorted['wealth_range']=[int(x*100/normalized_wealth_max) for x in df_last_allagents_sorted['normalized_wealth']]
    df_last_allagents_sorted['normalized_range']=df_last_allagents_sorted['normalized_wealth']
    df_last_allagents_mean=df_last_allagents_sorted.mean()
    df_last_range_count=pd.DataFrame(df_last_allagents_sorted.groupby('wealth_range').count()[0]).reindex(range(number_of_ranges),fill_value=0)
    df_last_range_count['frequency']=df_last_range_count[0]/df_last_range_count[0].sum()

    df_last_allagents_group=df_last_allagents_sorted.groupby('quantile').count().reindex(range(number_of_robots),fill_value=0)
    df_last_allagents_group['frequency']=df_last_allagents_group[0]/df_last_allagents_group[0].sum()
    df_last_allagents_group['cumulative_frequency']=df_last_allagents_group['frequency'].cumsum()
    df_last_allagents_group['anticumulated_frequency']=df_last_allagents_group.loc[::-1,'frequency'].cumsum()[::-1]

    df_last_meanagents_sorted=df_last.mean(axis=0).sort_values(ascending=True).to_frame()
    df_last_meanagents_sorted['relative_wealth']=df_last_meanagents_sorted/df_last_meanagents_sorted.sum()
    df_last_meanagents_sorted['cumulative_relative_wealth']=df_last_meanagents_sorted['relative_wealth'].cumsum()
    df_last_meanagents_sorted['anticumulated_relative_wealth']=df_last_meanagents_sorted.loc[::-1,'relative_wealth'].cumsum()[::-1]
    df_last_meanagents_sorted_mean=df_last_meanagents_sorted['relative_wealth'].mean()#use [0] for absolute wealth
    df_last_meanagents_sorted_dev=df_last_meanagents_sorted['relative_wealth'].std()
    poor_threshold=0.1
    rich_threshold=0.87
    selected_wealth_class=[]
    for agent_crw,agent_rw in zip(df_last_meanagents_sorted['cumulative_relative_wealth'],
                                df_last_meanagents_sorted['relative_wealth']):
        if agent_crw<=poor_threshold:# and agent_rw<df_last_meanagents_sorted_mean-0.8*df_last_meanagents_sorted_dev:
            selected_wealth_class.append('poor')
        elif agent_crw>=rich_threshold and agent_rw>df_last_meanagents_sorted_mean+0.8*df_last_meanagents_sorted_dev:
            selected_wealth_class.append('rich')
        else:
            selected_wealth_class.append('middle')
    df_last_meanagents_sorted['wealth_class']=selected_wealth_class

    df_last_meanagents_sorted['classile']=None
    df_last_meanagents_sorted['classile'][df_last_meanagents_sorted['wealth_class']=='poor']=poor_threshold
    df_last_meanagents_sorted['classile'][df_last_meanagents_sorted['wealth_class']=='rich']=rich_threshold
    quantiles=[poor_threshold+(poor_threshold+rich_threshold)/6,(poor_threshold+rich_threshold)/2,rich_threshold-(poor_threshold+rich_threshold)/6]
    assigned_quantiles=[]
    mid_len=len(df_last_meanagents_sorted['wealth_class'][df_last_meanagents_sorted['wealth_class']=='middle'])
    for l,_ in enumerate(df_last_meanagents_sorted['wealth_class'][df_last_meanagents_sorted['wealth_class']=='middle']):
        if l/mid_len<=1/len(quantiles):assigned_quantiles.append(quantiles[0])
        elif l/mid_len<=2/len(quantiles):assigned_quantiles.append(quantiles[1])
        else:assigned_quantiles.append(quantiles[2])
    df_last_meanagents_sorted['classile'][df_last_meanagents_sorted['wealth_class']=='middle']=assigned_quantiles
    df_last_meanagents_sorted['id']=[int(_.split('_')[-1]) for _ in df_last_meanagents_sorted.index.tolist()]
    df_last_meanagents_sorted['quantile']=range(number_of_robots)
    df_last_meanagents_sorted=df_last_meanagents_sorted.set_index('quantile')

    df_last_meanagents_classes=pd.DataFrame(df_last_meanagents_sorted.groupby('wealth_class',sort=False)[0].count())
    df_last_meanagents_classes['wealth_sum']=pd.DataFrame(df_last_meanagents_sorted.groupby('wealth_class')[0].sum())
    df_last_meanagents_classes['relative_wealth']=pd.DataFrame(df_last_meanagents_sorted.groupby('wealth_class')['relative_wealth'].sum())
    df_last_meanagents_classes['cumulative_relative_wealth']=df_last_meanagents_classes['relative_wealth'].cumsum()
    poor_ids=df_last_meanagents_sorted[df_last_meanagents_sorted['wealth_class']=='poor']['id'].tolist()
    middle_ids=df_last_meanagents_sorted[df_last_meanagents_sorted['wealth_class']=='middle']['id'].tolist()
    rich_ids=df_last_meanagents_sorted[df_last_meanagents_sorted['wealth_class']=='rich']['id'].tolist()
    df_last_meanagents_classes['ids']=[poor_ids,middle_ids,rich_ids]

    df_last_meanagents_extended_classes=pd.DataFrame(df_last_meanagents_sorted.groupby('classile',sort=False)[0].sum())
    df_last_meanagents_extended_classes['relative_wealth']=pd.DataFrame(df_last_meanagents_sorted.groupby('classile')['relative_wealth'].sum())
    
    #TODO wealth classes division with k-means clustering###########
    # kmeans=KMeans(3).fit(...)
    


    ################################################################
    
    #FREQUENCY PLOTS
    fig,ax=plt.subplots(figsize=(20,10))

    df_group_to_use=df_last_allagents_group
    y_label='frequency'
    if weight_by_group_wealth:
        y_label="group wealth-weighted "+y_label
        df_group_to_use['frequency'].iloc[:len(df_last_meanagents_classes['ids']['poor'])]=\
            df_group_to_use['frequency'].iloc[:len(df_last_meanagents_classes['ids']['poor'])]*\
            df_last_meanagents_classes['relative_wealth'].iloc[0]
        df_group_to_use['frequency'].iloc[len(df_last_meanagents_classes['ids']['poor']):\
            len(df_last_meanagents_classes['ids']['poor'])+len(df_last_meanagents_classes['ids']['middle'])]=\
            df_group_to_use['frequency'].iloc[len(df_last_meanagents_classes['ids']['poor']):\
            len(df_last_meanagents_classes['ids']['poor'])+len(df_last_meanagents_classes['ids']['middle'])]*\
            df_last_meanagents_classes['relative_wealth'].iloc[1]
        df_group_to_use['frequency'].iloc[len(df_last_meanagents_classes['ids']['poor'])+\
            len(df_last_meanagents_classes['ids']['middle']):]=\
            df_group_to_use['frequency'].iloc[len(df_last_meanagents_classes['ids']['poor'])+\
            len(df_last_meanagents_classes['ids']['middle']):]*\
            df_last_meanagents_classes['relative_wealth'].iloc[2]
        
    plt.title(f"wealth distribution and quantiles, with poor, mid and rich distinction for\n{filename}")
    plt.xlabel("quantile")
    plt.ylabel(y_label)
    sns.lineplot(x=df_group_to_use.index,y=df_group_to_use['frequency'],color='black')
    if number_of_saboteurs>1:
        plt.fill_between(df_group_to_use.index,df_group_to_use['frequency'],
                        where=(df_group_to_use.index>=0)&(df_group_to_use.index<=\
                                                                number_of_saboteurs-1),
                        color='blue',alpha=0.2)
    elif number_of_saboteurs==1:
        #NOTE 0 must be counted as a position. eg the interval [0,2] contains 3 poors
        plt.vlines(0,0,df_group_to_use['frequency'].iloc[0],color='blue',linewidth=10)

    if number_of_saboteurs!=len(df_last_meanagents_classes['ids']['poor']):
        if number_of_saboteurs<len(df_last_meanagents_classes['ids']['poor']):
            interval_min=number_of_saboteurs
            interval_max=len(df_last_meanagents_classes['ids']['poor'])
        elif number_of_saboteurs>len(df_last_meanagents_classes['ids']['poor']):
            interval_min=len(df_last_meanagents_classes['ids']['poor'])
            interval_max=number_of_saboteurs

        plt.fill_between(df_group_to_use.index,df_group_to_use['frequency'],
                        where=(df_group_to_use.index>=interval_min-1)&(df_group_to_use.index<=interval_max-1),
                        color='red',alpha=0.2)
    plt.fill_between(df_group_to_use.index,df_group_to_use['frequency'],
                        where=(df_group_to_use.index>=number_of_saboteurs-1)&\
                            (df_group_to_use.index<=len(df_last_meanagents_classes['ids']['poor'])+\
                            len(df_last_meanagents_classes['ids']['middle'])-1),
                        color='black',alpha=0.2)
    #NOTE point where rich red area starts must NOT be counted for number of rich. eg [22,24] contains 2 rich
    plt.fill_between(df_group_to_use.index,df_group_to_use['frequency'],
                        where=(df_group_to_use.index>=len(df_last_meanagents_classes['ids']['poor'])+\
                            len(df_last_meanagents_classes['ids']['middle'])-1)&\
                            (df_group_to_use.index<=len(df_last_meanagents_classes['ids']['poor'])+\
                            len(df_last_meanagents_classes['ids']['middle'])+\
                            len(df_last_meanagents_classes['ids']['rich'])-1),
                        color='red',alpha=0.2)
    
    #TODO IDEAL/UNWANTED CLASS EXTENSION: could color distribution loine instead
    # if number_of_saboteurs>0:
    #     plt.vlines(number_of_saboteurs-1,0,df_group_to_use['frequency'].max(),color='blue')
    # if len(df_last_meanagents_classes['ids']['poor'])>0:
    #     plt.vlines(len(df_last_meanagents_classes['ids']['poor'])-1,0,df_group_to_use['frequency'].max(),
    #                color='red',linestyles='dashed')
    # if len(df_last_meanagents_classes['ids']['rich'])>0:
    #     plt.vlines(len(df_last_meanagents_classes['ids']['poor']+df_last_meanagents_classes['ids']['middle'])-1,
    #                0,df_group_to_use['frequency'].max(),color='red',linestyles='dashed')

    #MEAN QUANTILE LINE
    plt.vlines(df_last_allagents_mean['quantile'],0,df_group_to_use['frequency'].max(),color='green',linestyles='dashed')
    plt.xticks(range(number_of_robots))
    wealth_class_text=f"mean quantile: {df_last_allagents_mean['quantile']:.2f}\n\nWEALTH CLASSES (relative wealth - numerosity):\n"
    for wealt_class in df_last_meanagents_classes.index:
        wealth_class_text+=f"{wealt_class.upper()}: {df_last_meanagents_classes.loc[wealt_class]['relative_wealth']:.2f}"
        wealth_class_text+=f" - {len(df_last_meanagents_classes.loc[wealt_class]['ids'])}"
        if wealt_class=='rich': wealth_class_text+=" (ideally 0)\n"
        elif wealt_class=='poor': wealth_class_text+=f" (ideally {number_of_saboteurs})\n"
        else: wealth_class_text+=f" (ideally {number_of_honest})\n"    
    plt.text(number_of_robots*.38,df_group_to_use['frequency'].max()*0.8,wealth_class_text)

    #ANTICUMULATED FREQUENCY PLOT
    twax=ax.twinx()
    sns.lineplot(x=df_last_allagents_group.index,y=df_last_allagents_group['anticumulated_frequency'],color='blue',alpha=0.2)
    plt.ylabel("Anticumulated quantile frequency")
    twax.spines['right'].set_color('blue')

    #MEAN WEALTH PER QUANTILE
    twax2=ax.twinx()
    sns.lineplot(x=df_last_meanagents_sorted.index,y=df_last_meanagents_sorted[0],color='green',alpha=0.2)
    plt.ylabel("quantile mean wealth")
    fig.subplots_adjust(right=0.88)
    twax2.spines['right'].set_position(('axes', 1.08))
    twax2.set_frame_on(True)
    twax2.patch.set_visible(False)
    twax2.spines['right'].set_color('green')

    if save_plot:
        plt.savefig(f"{save_folder}/{save_name}_wealth_distribution.png")
        plt.close()
    elif not multi_plot:
        plt.show()
    

#TODO inequality lorenz/gini also without agent aggregation
def market_lorenz_gini(filename:str,#
                        data_folder_and_subfolder:str="",
                        metric:str="reward_evolution",
                        number_of_robots:int=25,
                        equally_sized_honest_groups=False,
                        multi_plot:bool=False,
                        pair_plot:bool=False,
                        fill_between:bool=False,
                        individual_group_sum:bool=True,
                        compute_ideal:bool=False,
                        save_plot:bool=False,
                        save_folder:str="",
                        save_name:str="",
                        ):
    '''
    compute lorenz wealth distribution curve and the relative gini coefficient
    in a market where agents may have negative wealth

    also show the presence of an oligarchy of an agent, in the case it has more that
    a certain percentage of the total wealth (default 10%)

    gini coefficient is the area between the lorenz curve and the line
    of perfect equality (the diagonal line); in case of oligarchy, the coefficient must be
    corrected.

    Gini coeff is usually between 0 and 1, but can be greater if the number of negative wealth
    agents is large enough

    :param compute_ideal: if True, compute the ideal curve based
      on the number of byzantine agents: in this case, they should have zero wealth/reward;
      everyone else should have the same wealth/reward, namely:
        initial_wealth_per_agent +sum_of_byzantine_wealth/number_of_honest_agents

    '''
    if 'reward' in metric:
        metric="rewards_evolution"
    elif 'wealth' in metric:
        metric="wealth_evolution"

    params=params_from_filename(filename,compact_format=True)
    title_params=params_from_filename(filename)
    title=f"{title_params[0]}honest {BEHAVIORS_NAME_DICT[params[1]]},{title_params[5]} lie angle,"\
    f"{'reputation' if params[4] and params[3]=='P' else ''} {'staking' if params[3]=='P' else 'no staking'}\n"\
    f"noise: {title_params[7]}\n behaviour params: {title_params[6]}".replace(",",", ")

    number_of_honest=int(params[0])
    number_of_saboteurs=number_of_robots-number_of_honest
    saboteur_performance=params[7][2]

    if compute_ideal:
        if "IM" in data_folder_and_subfolder or "IM" in filename:
            initial_wealth_per_agent=7
        elif "IFM" in data_folder_and_subfolder or "IFM" in filename:
            initial_wealth_per_agent=1

        byzantine_wealth=0
        honest_wealth=initial_wealth_per_agent+initial_wealth_per_agent*number_of_saboteurs/number_of_honest
        ideal_wealths=[byzantine_wealth]*number_of_saboteurs+[honest_wealth]*number_of_honest
        df_last_allagents_mean_sorted=pd.Series(ideal_wealths,index=range(number_of_robots))

    else:
        df=dataframe_from_csv(join(data_folder_and_subfolder,metric,filename),
                                metric=metric,experiment_part="df")
        # sim_col=df.columns.to_list()[0]
        # tick_col=df.columns.to_list()[1]
        # agent_col=df.columns.to_list()[2:]
        # selected_runs=df[df.columns.to_list()[0]].unique()
        selected_ticks=df[df.columns.to_list()[1]].unique()
        # df_reference_initial=pd.Series(7,index=selected_ticks)
        df_last=df[df['tick']==selected_ticks.max()].drop(columns=['tick','simulation_id'])
        df_last_allagents_mean_sorted=df_last.mean(axis=0).sort_values(ascending=True)

    #LORENZ CURVE AND GINI COEFFICIENT
    df_cumsum=df_last_allagents_mean_sorted.cumsum()
    df_cumsum=pd.DataFrame(pd.concat([pd.Series([0]),df_cumsum])).reset_index()
    df_cumsum.columns=['Fi','cumsum']
    df_cumsum['Fi']=df_cumsum.index/(len(df_cumsum)-1)
    df_cumsum['Si']=df_cumsum['cumsum']/len(df_cumsum)
    df_cumsum['Li']=df_cumsum['Si']/df_cumsum['Si'].iloc[-1]

    #expressed in fraction of total wealth
    MIN_OLIGARCH_DIFF=.1
    if df_cumsum['Li'].iloc[-1]-df_cumsum['Li'].iloc[-2]>MIN_OLIGARCH_DIFF:
        oligarch_exists=True
        df_cumsum['Fi']=df_cumsum['Fi']*len(df_cumsum-1)
        df_cumsum['Fi']=df_cumsum['Fi']/(len(df_cumsum)-2)
        df_cumsum['Fi']=df_cumsum['Fi']/df_cumsum['Fi'].iloc[-2]
        df_oligarch=df_cumsum.iloc[-1]
        df_cumsum=df_cumsum.iloc[:-1]
    else:
        oligarch_exists=False

    zero_crossing = np.where(np.diff(np.sign(df_cumsum['Li'].to_list())))[0][-1]
    #####simpsons 3/8 rule
    # a=df_cumsum['Fi'].iloc[zero_crossing]
    # b=df_cumsum['Fi'].iloc[-1]
    # hh=(b-a)/len(df_cumsum['Fi'].iloc[zero_crossing:])
    # f_a=df_cumsum['Li'].iloc[zero_crossing]
    # f_b=df_cumsum['Li'].iloc[-1]
    # try:
    #     #c1=(2a+b)/3
    #     print(df_cumsum.index[abs(df_cumsum['Fi']-(2*a+b)/3)<0.01].tolist())
    #     print(df_cumsum['Fi'])
    #     print((2*a+b)/3)
    #     c1=df_cumsum.index[abs(df_cumsum['Fi']-(2*a+b)/3)<0.01].tolist()[-1]
    #     f_c1=df_cumsum['Li'].iloc[c1]
    # except IndexError:
    #     f_c1=0
    # try:
    #     #c2=(a+2b)/3
    #     print(df_cumsum.index[abs(df_cumsum['Fi']-(a+2*b)/3)<0.01].tolist())
    #     c2=df_cumsum.index[abs(df_cumsum['Fi']-(a+2*b)/3)<0.01].tolist()[-1]
    #     f_c2=df_cumsum['Li'].iloc[c2]
    # except IndexError:
    #     f_c2=0
    # B=3*hh/8*(f_a+3*f_c1+3*f_c2+f_b)

    #####composite trapzoid rule
    a=df_cumsum['Fi'].iloc[zero_crossing]
    b=df_cumsum['Fi'].iloc[-1]
    h=(b-a)/len(df_cumsum['Fi'].iloc[zero_crossing:])
    B=0
    for ii,_ in enumerate(df_cumsum['Fi'].iloc[zero_crossing:-1]):
        li=df_cumsum['Li'].iloc[zero_crossing+ii]
        li_next=df_cumsum['Li'].iloc[zero_crossing+ii+1]
        B+=h/2*(li+li_next)

    if df_cumsum['Li'].min()<0:
        # if oligarch_exists:
        a=df_cumsum['Fi'].iloc[0]
        b=df_cumsum['Fi'].iloc[zero_crossing-1 if zero_crossing>0 else 0]
        h=(b-a)/len(df_cumsum['Fi'].iloc[:zero_crossing-1 if zero_crossing>0 else 0])
        C=0
        for ii,_ in enumerate(df_cumsum['Fi'].iloc[:zero_crossing-1 if zero_crossing>0 else 0]):
            li=df_cumsum['Li'].iloc[ii]
            li_next=df_cumsum['Li'].iloc[ii+1]
            C+=h/2*abs(li+li_next)
        #Gini coeff = (A-C)/(A-C +B)
        Gini=(1-2*(B+C))/(1-2*C)
        # else:
        #     #Gini coeff = A/(A+B)
        #     Gini=(1-2*B)
    else:
        #Gini coeff = A/(A+B)
        Gini=(1-2*B)

    plt.figure(figsize=(10,10))
    plt.plot([0,1],[0,1],color='black',linewidth=1)#EQUALITY CURVE
    sns.lineplot(data=df_cumsum,x=df_cumsum['Fi'], y=df_cumsum['Li'],color='red',linewidth=2)#LORENZ CURVE
    plt.fill_between(df_cumsum['Fi'],df_cumsum['Li'],color='red',alpha=0.2)#LORENZ CURVE AREA
    #TODO add dots/lines/whatever below the curve, to represent where each robot of each noise group is
    #       in the distribution of wealth
    plt.title(f"{params}\nLorenz Curve and Gini Coefficient: {metric.replace('_',' ')}")
    plt.xlabel("Percentage of Agents")
    plt.ylabel("Percentage of Wealth")
    plt.legend(['Equality','Lorenz Curve'])
    plt.text(0.4,0.65,f"G: {round(Gini,3)}\nB: {round(B,3)}\nC: {round(C,3) if df_cumsum['Li'].min()<0 else 'N/A'}",
             horizontalalignment='center',verticalalignment='center',transform=plt.gca().transAxes)
    # plt.text(0.4,0.65,f"Gini Coefficient: {round(Gini,3)}",horizontalalignment='center',verticalalignment='center',transform=plt.gca().transAxes)
    if oligarch_exists:
        plt.text(1,1-(df_oligarch['Li']-df_cumsum['Li'].iloc[-1])/2+.01,r"}",fontsize=50,fontweight='normal',
                 horizontalalignment='right',verticalalignment='top',transform=plt.gca().transAxes)
        plt.text(1.085,1-(df_oligarch['Li']-df_cumsum['Li'].iloc[-1])/2+.01,f"oligarchy\n{round(100*(df_oligarch['Li']-df_cumsum['Li'].iloc[-1]))}%",
                    horizontalalignment='right',verticalalignment='top',transform=plt.gca().transAxes)

    if save_plot:
        plt.savefig(f"{save_folder}/{save_name}_gini.png")
        plt.close()

    if not multi_plot and not save_plot:plt.show()

    # mytext=filename+"\nG:"+str(round(Gini,3))+", B:"+str(round(B,3))+", C:"+(str(round(C,3)) if oligarch_exists else "N/A")+"\n\n"
    # with open("/home/uga/Scrivania/gini.txt","a") as textfile:
    #     textfile.write(mytext)


def target_lorenz_gini(number_of_robots:int=25,
                        number_of_saboteurs:int=0,
                        multi_plot:bool=False,
                        ideal_scenario:bool=True,
                        market_type:str="IM-D",
                        save_plot:bool=False,
                        save_folder:str="",
                        save_name:str="",
                        ):
    '''
    compute lorenz wealth distribution curve and the relative gini coefficient
    for a target scenario where agents may have negative wealth

    gini coefficient is the area between the lorenz curve and the line
    of perfect equality (the diagonal line); in case of oligarchy, the coefficient must be
    corrected.

    Gini coeff is usually between 0 and 1, but can be greater if the number of negative wealth
    agents is large enough

    :param ideal_scenario: scenario to be tested. Possible values:
    - True (ideal): all byzantines have no wealth, all honests have equally distributed wealth.
    - False (real): byzantines retain a small amount of wealth, distributed according to
     #TODO SOME distribution, higly penalizing all except the (1+) richest poors;
      honests have wealth distributed according to a #TODO SOME distribution which
      penalizes greatly rich agents. Wealth positivity is prescribed by the market type.
    -"oligarchy": NOT IMPLEMENTED

    NOTE: real situations may be dependent by the parameters of market, behavior,...
        yet, it is considered independent from this (namely, averaging between all real situations)

    :param market_type: in the shape of m-d, where m is the income source(s) and
                            d is the default system
    Possible values for m:
    - "IM": information market (no foraging income)
    - "IFM": information and foraging market

    Possible values for d:
    - "D": deafult is permitted, no negative wealth allowed
    - "ND": no default is permitted, negative wealth allowed

    NOTE: "-" in the value string can be omitted

    '''
    # line_width=1

    if 'reward' in metric:
        metric="rewards_evolution"
    elif 'wealth' in metric:
        metric="wealth_evolution"

    title=f"ideal situation for {number_of_robots} robots and {number_of_honest} honests"

    number_of_honest=number_of_robots-number_of_saboteurs

    if ideal_scenario:
        if "IM" in market_type:
            initial_wealth_per_agent=7
        elif "IFM" in market_type:
            initial_wealth_per_agent=1

        byzantine_wealth=0
        honest_wealth=initial_wealth_per_agent+initial_wealth_per_agent*number_of_saboteurs/number_of_honest
        wealths=[byzantine_wealth]*number_of_saboteurs+[honest_wealth]*number_of_honest

    else:
        #TODO
        pass

    df_last_allagents_mean_sorted=pd.Series(wealths,index=range(number_of_robots))

    #LORENZ CURVE AND GINI COEFFICIENT
    df_cumsum=df_last_allagents_mean_sorted.cumsum()
    df_cumsum=pd.DataFrame(pd.concat([pd.Series([0]),df_cumsum])).reset_index()
    df_cumsum.columns=['Fi','cumsum']
    df_cumsum['Fi']=df_cumsum.index/(len(df_cumsum)-1)
    df_cumsum['Si']=df_cumsum['cumsum']/len(df_cumsum)
    df_cumsum['Li']=df_cumsum['Si']/df_cumsum['Si'].iloc[-1]

    MIN_OLIGARCH_DIFF=.1
    if df_cumsum['Li'].iloc[-1]-df_cumsum['Li'].iloc[-2]>MIN_OLIGARCH_DIFF:
        oligarch_exists=True
        df_cumsum['Fi']=df_cumsum['Fi']*len(df_cumsum-1)
        df_cumsum['Fi']=df_cumsum['Fi']/(len(df_cumsum)-2)
        df_cumsum['Fi']=df_cumsum['Fi']/df_cumsum['Fi'].iloc[-2]
        df_oligarch=df_cumsum.iloc[-1]
        df_cumsum=df_cumsum.iloc[:-1]
    else:
        oligarch_exists=False

    zero_crossing = np.where(np.diff(np.sign(df_cumsum['Li'].to_list())))[0][-1]

    #####composite trapzoid rule
    a=df_cumsum['Fi'].iloc[zero_crossing]
    b=df_cumsum['Fi'].iloc[-1]
    h=(b-a)/len(df_cumsum['Fi'].iloc[zero_crossing:])
    B=0
    for ii,_ in enumerate(df_cumsum['Fi'].iloc[zero_crossing:-1]):
        li=df_cumsum['Li'].iloc[zero_crossing+ii]
        li_next=df_cumsum['Li'].iloc[zero_crossing+ii+1]
        B+=h/2*(li+li_next)

    if df_cumsum['Li'].min()<0:
        # if oligarch_exists:
        a=df_cumsum['Fi'].iloc[0]
        b=df_cumsum['Fi'].iloc[zero_crossing-1 if zero_crossing>0 else 0]
        h=(b-a)/len(df_cumsum['Fi'].iloc[:zero_crossing-1 if zero_crossing>0 else 0])
        C=0
        for ii,_ in enumerate(df_cumsum['Fi'].iloc[:zero_crossing-1 if zero_crossing>0 else 0]):
            li=df_cumsum['Li'].iloc[ii]
            li_next=df_cumsum['Li'].iloc[ii+1]
            C+=h/2*abs(li+li_next)
        #Gini coeff = (A-C)/(A-C +B)
        Gini=(1-2*(B+C))/(1-2*C)
        # else:
        #     #Gini coeff = A/(A+B)
        #     Gini=(1-2*B)
    else:
        #Gini coeff = A/(A+B)
        Gini=(1-2*B)

    plt.figure(figsize=(10,10))
    plt.plot([0,1],[0,1],color='black',linewidth=1)
    sns.lineplot(data=df_cumsum,x=df_cumsum['Fi'], y=df_cumsum['Li'],color='red',linewidth=2)
    plt.fill_between(df_cumsum['Fi'],df_cumsum['Li'],color='red',alpha=0.2)
    plt.title(title)
    plt.xlabel("Percentage of Agents")
    plt.ylabel("Percentage of Wealth")
    plt.legend(['Equality','Lorenz Curve'])
    plt.text(0.4,0.65,f"G: {round(Gini,3)}\nB: {round(B,3)}\nC: {round(C,3) if oligarch_exists else 'N/A'}",
             horizontalalignment='center',verticalalignment='center',transform=plt.gca().transAxes)
    if oligarch_exists:
        plt.text(1,1-(df_oligarch['Li']-df_cumsum['Li'].iloc[-1])/2+.01,r"}",fontsize=50,fontweight='normal',
                 horizontalalignment='right',verticalalignment='top',transform=plt.gca().transAxes)
        plt.text(1.085,1-(df_oligarch['Li']-df_cumsum['Li'].iloc[-1])/2+.01,f"oligarchy\n{round(100*(df_oligarch['Li']-df_cumsum['Li'].iloc[-1]))}%",
                    horizontalalignment='right',verticalalignment='top',transform=plt.gca().transAxes)

    if save_plot:
        plt.savefig(f"{save_folder}/{save_name}_gini.png")
        plt.close()

    if not multi_plot and not save_plot:plt.show()


def buyers_sellers_groups(  filename:str,
                            data_folder_and_subfolder:str="",
                            number_of_robots:int=25,
                            multi_plot:bool=False,
                            equally_sized_honest_groups=False,
                            separate_groups=True,
                            show_variance:bool=False,
                            # x_labels=[],
                            # pair_plot:bool=False,
                            save_plot:bool=False,
                            save_folder:str="",
                            save_name:str="",
                            ):
    """
    TODO missing data for individual values of buys/sells for each group
    TODO buyers_sellers_groups docstring

    plost mean/median amount of transactions for each group

    subplot1(): buys for each group (combined/validated)
    subplot2: sells for each group (combined/validated)
    subplot3: ratio buys/sells (combined/validated)
        this last should be low for good, average for bad, high for saboteurs
    
    :param equally_sized_honest_groups: if True, the honest robots are divided in
            equally sized groups even for perfect saboteurs (as in the average sab. case).
    """
    if filename.endswith(".csv"):filename=filename.split(".csv")[0]

    params=params_from_filename(filename,compact_format=True)
    title_params=params_from_filename(filename)
    title=f"{title_params[0]}honest {BEHAVIORS_NAME_DICT[params[1]]},{title_params[5]} lie angle,"\
    f"{'reputation' if params[4] and params[3]=='P' else ''} {'staking' if params[3]=='P' else 'no staking'}\n"\
    f"noise: {title_params[7]}\n behaviour params: {title_params[6]}".replace(",",", ")

    # number_of_robots=len(df.colums)
    number_of_honest=int(params[0])
    number_of_saboteurs=number_of_robots-number_of_honest
    saboteur_performance=params[7][2]

    good_slice,bad_slice=noise_groups_slices(number_of_robots,number_of_saboteurs,
                                        saboteur_performance if not equally_sized_honest_groups else "bypass")

    # sellers_to_good_list=[]
    # sellers_to_bad_list=[]
    # #if bad_slice is not None:sellers_to_sab_list=[]
    # if number_of_saboteurs>0:
    # if separate_groups:
    #     #if bad_slice is not None:
    #     if number_of_saboteurs>0:
    #         sellers_to_good_list=[[],[],[]]
    #         sellers_to_bad_list=[[],[],[]]
    #         sellers_to_sab_list=[[],[],[]]
    #     else:
    #         sellers_to_good_list=[[],[]]
    #         sellers_to_bad_list=[[],[]]

    denominator_trans="validated"
    numerator_trans="combined"
    data_folder_and_subfolder=join(data_folder_and_subfolder,"transactions")
    f_buys_num=f"{filename}_{numerator_trans}_buyer.csv"
    f_buys_den=f"{filename}_{denominator_trans}_buyer.csv"
    f_sells_num=f"{filename}_{numerator_trans}_seller.csv"
    f_sells_den=f"{filename}_{denominator_trans}_seller.csv"

    df_buys_num=dataframe_from_csv(filename=f_buys_num,data_folder_and_subfolder=data_folder_and_subfolder,metric="transaction")
    df_buys_den=dataframe_from_csv(filename=f_buys_den,data_folder_and_subfolder=data_folder_and_subfolder,metric="transaction")
    df_buys=100*df_buys_num/df_buys_den
    df_buys_good_ratio=100*(df_buys.iloc[:,:good_slice].sum(axis=0)/df_buys.sum(axis=0)).mean().round(3)*good_slice/number_of_robots
    df_buys_bad_ratio=100*(df_buys.iloc[:,good_slice:bad_slice].sum(axis=0)/df_buys.sum(axis=0)).mean().round(3)*(bad_slice-good_slice)/number_of_robots
    if number_of_saboteurs>0:
        df_buys_sab_ratio=100*(df_buys.iloc[:,bad_slice:].sum(axis=0)/df_buys.sum(axis=0)).mean().round(3)*(number_of_saboteurs)/number_of_robots
    df_buys_mean=df_buys.mean(axis=0)
    df_buys_median=df_buys.median(axis=0)
    df_buys_var=df_buys.var(axis=0)
    df_buys_max=df_buys.max(axis=0)
    df_buys_min=df_buys.min(axis=0)
    df_sells_num=dataframe_from_csv(filename=f_sells_num,data_folder_and_subfolder=data_folder_and_subfolder,metric="transaction")
    df_sells_den=dataframe_from_csv(filename=f_sells_den,data_folder_and_subfolder=data_folder_and_subfolder,metric="transaction")
    df_sells=100*df_sells_num/df_sells_den
    df_sells_good_ratio=100*(df_sells.iloc[:,:good_slice].sum(axis=0)/df_sells.sum(axis=0)).mean().round(3)*good_slice/number_of_robots
    df_sells_bad_ratio=100*(df_sells.iloc[:,good_slice:bad_slice].sum(axis=0)/df_sells.sum(axis=0)).mean().round(3)*(bad_slice-good_slice)/number_of_robots
    if number_of_saboteurs>0:
        df_sells_sab_ratio=100*(df_sells.iloc[:,bad_slice:].sum(axis=0)/df_sells.sum(axis=0)).mean().round(3)*(number_of_saboteurs)/number_of_robots
    
    #TODO I DONT WANT SELLS AND BUYS RATIO TO BE THE SAME: good: sell more, bad,sab: buy more
    # print('good',df_buys_good_ratio==df_sells_good_ratio)
    # print('bad',df_buys_bad_ratio==df_sells_bad_ratio)
    # if number_of_saboteurs>0:
    #     print('sab',df_sells_sab_ratio==df_buys_sab_ratio)
    # print()
    # return

    df_sells_mean=df_sells.mean(axis=0)
    df_sells_median=df_sells.median(axis=0)
    df_sells_var=df_sells.var(axis=0)
    df_sells_max=df_sells.max(axis=0)
    df_sells_min=df_sells.min(axis=0)
    df_buys_mean_good=df_buys_mean[:good_slice]
    df_buys_median_good=df_buys_median[:good_slice]
    df_buys_mean_good_mean=pd.DataFrame(pd.Series(df_buys_mean_good.mean()))
    df_buys_median_good_mean=pd.DataFrame(pd.Series(df_buys_median_good.mean()))
    df_buys_mean_good_mean['plot_order']=0
    df_buys_median_good_mean['plot_order']=1
    df_buys_mean_good=pd.concat([df_buys_mean_good_mean,df_buys_median_good_mean])
    df_buys_var_good=df_buys_var[0:good_slice]
    df_buys_var_good_max=pd.DataFrame(pd.Series(df_buys_var_good.max()))
    df_buys_var_good_mean=pd.DataFrame(pd.Series(df_buys_var_good.mean()))
    df_buys_var_good_min=pd.DataFrame(pd.Series(df_buys_var_good.min()))
    df_buys_var_good_max['plot_order']=0
    df_buys_var_good_mean['plot_order']=1
    df_buys_var_good_min['plot_order']=2
    df_buys_var_good=pd.concat([df_buys_var_good_max,df_buys_var_good_mean,df_buys_var_good_min])
    df_buys_max_good=df_buys_max[0:good_slice]
    df_buys_max_good_mean=pd.DataFrame(pd.Series(df_buys_max_good.mean()))
    df_buys_max_good_max=pd.DataFrame(pd.Series(df_buys_max_good.max()))
    df_buys_max_good_mean['plot_order']=0
    df_buys_max_good_max['plot_order']=1
    df_buys_max_good=pd.concat([df_buys_max_good_mean,df_buys_max_good_max])
    df_buys_min_good=df_buys_min[0:good_slice]
    df_buys_min_good_mean=pd.DataFrame(pd.Series(df_buys_min_good.mean()))
    df_buys_min_good_min=pd.DataFrame(pd.Series(df_buys_min_good.min()))
    df_buys_min_good_mean['plot_order']=0
    df_buys_min_good_min['plot_order']=1
    df_buys_min_good=pd.concat([df_buys_min_good_mean,df_buys_min_good_min])
    df_buys_mean_bad=df_buys_mean[good_slice:bad_slice]
    df_buys_median_bad=df_buys_median[good_slice:bad_slice]
    df_buys_mean_bad_mean=pd.DataFrame(pd.Series(df_buys_mean_bad.mean()))
    df_buys_median_bad_mean=pd.DataFrame(pd.Series(df_buys_median_bad.mean()))
    df_buys_mean_bad_mean['plot_order']=0
    df_buys_median_bad_mean['plot_order']=1
    df_buys_mean_bad=pd.concat([df_buys_mean_bad_mean,df_buys_median_bad_mean])
    df_buys_var_bad=df_buys_var[good_slice:bad_slice]
    df_buys_var_bad_max=pd.DataFrame(pd.Series(df_buys_var_bad.max()))
    df_buys_var_bad_mean=pd.DataFrame(pd.Series(df_buys_var_bad.mean()))
    df_buys_var_bad_min=pd.DataFrame(pd.Series(df_buys_var_bad.min()))
    df_buys_var_bad_max['plot_order']=0
    df_buys_var_bad_mean['plot_order']=1
    df_buys_var_bad_min['plot_order']=2
    df_buys_var_bad=pd.concat([df_buys_var_bad_max,df_buys_var_bad_mean,df_buys_var_bad_min])
    df_buys_max_bad=df_buys_max[good_slice:bad_slice]
    df_buys_max_bad_mean=pd.DataFrame(pd.Series(df_buys_max_bad.mean()))
    df_buys_max_bad_max=pd.DataFrame(pd.Series(df_buys_max_bad.max()))
    df_buys_max_bad_mean['plot_order']=0
    df_buys_max_bad_max['plot_order']=1
    df_buys_max_bad=pd.concat([df_buys_max_bad_mean,df_buys_max_bad_max])
    df_buys_min_bad=df_buys_min[good_slice:bad_slice]
    df_buys_min_bad_mean=pd.DataFrame(pd.Series(df_buys_min_bad.mean()))
    df_buys_min_bad_min=pd.DataFrame(pd.Series(df_buys_min_bad.min()))
    df_buys_min_bad_mean['plot_order']=0
    df_buys_min_bad_min['plot_order']=1
    df_buys_min_bad=pd.concat([df_buys_min_bad_mean,df_buys_min_bad_min])
    df_sells_mean_good=df_sells_mean[:good_slice]
    df_sells_median_good=df_sells_median[:good_slice]
    df_sells_mean_good_mean=pd.DataFrame(pd.Series(df_sells_mean_good.mean()))
    df_sells_median_good_mean=pd.DataFrame(pd.Series(df_sells_median_good.mean()))
    df_sells_mean_good_mean['plot_order']=0
    df_sells_median_good_mean['plot_order']=1
    df_sells_mean_good=pd.concat([df_sells_mean_good_mean,df_sells_median_good_mean])
    df_sells_var_good=df_sells_var[0:good_slice]
    df_sells_var_good_max=pd.DataFrame(pd.Series(df_sells_var_good.max()))
    df_sells_var_good_mean=pd.DataFrame(pd.Series(df_sells_var_good.mean()))
    df_sells_var_good_min=pd.DataFrame(pd.Series(df_sells_var_good.min()))
    df_sells_var_good_max['plot_order']=0
    df_sells_var_good_mean['plot_order']=1
    df_sells_var_good_min['plot_order']=2
    df_sells_var_good=pd.concat([df_sells_var_good_max,df_sells_var_good_mean,df_sells_var_good_min])
    df_sells_max_good=df_sells_max[:good_slice]
    df_sells_max_good_mean=pd.DataFrame(pd.Series(df_sells_max_good.mean()))
    df_sells_max_good_max=pd.DataFrame(pd.Series(df_sells_max_good.max()))
    df_sells_max_good_mean['plot_order']=0
    df_sells_max_good_max['plot_order']=1
    df_sells_max_good=pd.concat([df_sells_max_good_mean,df_sells_max_good_max])
    df_sells_min_good=df_sells_min[0:good_slice]
    df_sells_min_good_mean=pd.DataFrame(pd.Series(df_sells_min_good.mean()))
    df_sells_min_good_min=pd.DataFrame(pd.Series(df_sells_min_good.min()))
    df_sells_min_good_mean['plot_order']=0
    df_sells_min_good_min['plot_order']=1
    df_sells_min_good=pd.concat([df_sells_min_good_mean,df_sells_min_good_min])
    df_sells_mean_bad=df_sells_mean[good_slice:bad_slice]
    df_sells_median_bad=df_sells_median[good_slice:bad_slice]
    df_sells_mean_bad_mean=pd.DataFrame(pd.Series(df_sells_mean_bad.mean()))
    df_sells_median_bad_mean=pd.DataFrame(pd.Series(df_sells_median_bad.mean()))
    df_sells_mean_bad_mean['plot_order']=0
    df_sells_median_bad_mean['plot_order']=1
    df_sells_mean_bad=pd.concat([df_sells_mean_bad_mean,df_sells_median_bad_mean])
    df_sells_var_bad=df_sells_var[good_slice:bad_slice]
    df_sells_var_bad_max=pd.DataFrame(pd.Series(df_sells_var_bad.max()))
    df_sells_var_bad_mean=pd.DataFrame(pd.Series(df_sells_var_bad.mean()))
    df_sells_var_bad_min=pd.DataFrame(pd.Series(df_sells_var_bad.min()))
    df_sells_var_bad_max['plot_order']=0
    df_sells_var_bad_mean['plot_order']=1
    df_sells_var_bad_min['plot_order']=2
    df_sells_var_bad=pd.concat([df_sells_var_bad_max,df_sells_var_bad_mean,df_sells_var_bad_min])
    df_sells_max_bad=df_sells_max[good_slice:bad_slice]
    df_sells_max_bad_mean=pd.DataFrame(pd.Series(df_sells_max_bad.mean()))
    df_sells_max_bad_max=pd.DataFrame(pd.Series(df_sells_max_bad.max()))
    df_sells_max_bad_mean['plot_order']=0
    df_sells_max_bad_max['plot_order']=1
    df_sells_max_bad=pd.concat([df_sells_max_bad_mean,df_sells_max_bad_max])
    df_sells_min_bad=df_sells_min[good_slice:bad_slice]
    df_sells_min_bad_mean=pd.DataFrame(pd.Series(df_sells_min_bad.mean()))
    df_sells_min_bad_min=pd.DataFrame(pd.Series(df_sells_min_bad.min()))
    df_sells_min_bad_mean['plot_order']=0
    df_sells_min_bad_min['plot_order']=1
    df_sells_min_bad=pd.concat([df_sells_min_bad_mean,df_sells_min_bad_min])
    df_sells_good_ratio=pd.DataFrame(pd.Series(df_sells_good_ratio))
    df_sells_good_ratio['plot_order']=0
    df_sells_bad_ratio=pd.DataFrame(pd.Series(df_sells_bad_ratio))
    df_sells_bad_ratio['plot_order']=1
    df_buys_good_ratio=pd.DataFrame(pd.Series(df_buys_good_ratio))
    df_buys_good_ratio['plot_order']=0
    df_buys_bad_ratio=pd.DataFrame(pd.Series(df_buys_bad_ratio))
    df_buys_bad_ratio['plot_order']=1
    if number_of_saboteurs>0:
        df_buys_mean_sab=df_buys_mean[bad_slice:]
        df_buys_median_sab=df_buys_median[bad_slice:]
        df_buys_mean_sab_mean=pd.DataFrame(pd.Series(df_buys_mean_sab.mean()))
        df_buys_median_sab_mean=pd.DataFrame(pd.Series(df_buys_median_sab.mean()))
        df_buys_mean_sab_mean['plot_order']=0
        df_buys_median_sab_mean['plot_order']=1
        df_buys_mean_sab=pd.concat([df_buys_mean_sab_mean,df_buys_median_sab_mean])
        df_buys_var_sab=df_buys_var[bad_slice:]
        df_buys_var_sab_max=pd.DataFrame(pd.Series(df_buys_var_sab.max()))
        df_buys_var_sab_mean=pd.DataFrame(pd.Series(df_buys_var_sab.mean()))
        df_buys_var_sab_min=pd.DataFrame(pd.Series(df_buys_var_sab.min()))
        df_buys_var_sab_max['plot_order']=0
        df_buys_var_sab_mean['plot_order']=1
        df_buys_var_sab_min['plot_order']=2
        df_buys_var_sab=pd.concat([df_buys_var_sab_max,df_buys_var_sab_mean,df_buys_var_sab_min])
        df_buys_max_sab=df_buys_max[bad_slice:]
        df_buys_max_sab_mean=pd.DataFrame(pd.Series(df_buys_max_sab.mean()))
        df_buys_max_sab_max=pd.DataFrame(pd.Series(df_buys_max_sab.max()))
        df_buys_max_sab_mean['plot_order']=0
        df_buys_max_sab_max['plot_order']=1
        df_buys_max_sab=pd.concat([df_buys_max_sab_mean,df_buys_max_sab_max])
        df_buys_min_sab=df_buys_min[bad_slice:]
        df_buys_min_sab_mean=pd.DataFrame(pd.Series(df_buys_min_sab.mean()))
        df_buys_min_sab_min=pd.DataFrame(pd.Series(df_buys_min_sab.min()))
        df_buys_min_sab_mean['plot_order']=0
        df_buys_min_sab_min['plot_order']=1
        df_buys_min_sab=pd.concat([df_buys_min_sab_mean,df_buys_min_sab_min])
        df_sells_mean_sab=df_sells_mean[bad_slice:]
        df_sells_median_sab=df_sells_median[bad_slice:]
        df_sells_mean_sab_mean=pd.DataFrame(pd.Series(df_sells_mean_sab.mean()))
        df_sells_median_sab_mean=pd.DataFrame(pd.Series(df_sells_median_sab.mean()))
        df_sells_mean_sab_mean['plot_order']=0
        df_sells_median_sab_mean['plot_order']=1
        df_sells_mean_sab=pd.concat([df_sells_mean_sab_mean,df_sells_median_sab_mean])
        df_sells_var_sab=df_sells_var[bad_slice:]
        df_sells_var_sab_max=pd.DataFrame(pd.Series(df_sells_var_sab.max()))
        df_sells_var_sab_mean=pd.DataFrame(pd.Series(df_sells_var_sab.mean()))
        df_sells_var_sab_min=pd.DataFrame(pd.Series(df_sells_var_sab.min()))
        df_sells_var_sab_max['plot_order']=0
        df_sells_var_sab_mean['plot_order']=1
        df_sells_var_sab_min['plot_order']=2
        df_sells_var_sab=pd.concat([df_sells_var_sab_max,df_sells_var_sab_mean,df_sells_var_sab_min])
        df_sells_max_sab=df_sells_max[bad_slice:]
        df_sells_max_sab_mean=pd.DataFrame(pd.Series(df_sells_max_sab.mean()))
        df_sells_max_sab_max=pd.DataFrame(pd.Series(df_sells_max_sab.max()))
        df_sells_max_sab_mean['plot_order']=0
        df_sells_max_sab_max['plot_order']=1
        df_sells_max_sab=pd.concat([df_sells_max_sab_mean,df_sells_max_sab_max])
        df_sells_min_sab=df_sells_min[bad_slice:]
        df_sells_min_sab_mean=pd.DataFrame(pd.Series(df_sells_min_sab.mean()))
        df_sells_min_sab_min=pd.DataFrame(pd.Series(df_sells_min_sab.min()))
        df_sells_min_sab_mean['plot_order']=0
        df_sells_min_sab_min['plot_order']=1
        df_sells_min_sab=pd.concat([df_sells_min_sab_mean,df_sells_min_sab_min])
        df_sells_sab_ratio=pd.DataFrame(pd.Series(df_sells_sab_ratio.mean()))
        df_sells_sab_ratio['plot_order']=2
        df_buys_sab_ratio=pd.DataFrame(pd.Series(df_buys_sab_ratio.mean()))
        df_buys_sab_ratio['plot_order']=2

    fig,axs=plt.subplots(2,5 if show_variance else 4, figsize=(15,10))#with relative percentages
    # fig,axs=plt.subplots(2,4 if show_variance else 3, figsize=(15,10))
    plt.subplots_adjust(bottom=0.05,top=0.88,left=0.05,right=0.98,wspace=None,hspace=0.1)
    plt.suptitle(title,fontweight='bold')

    sns.pointplot(data=pd.melt(df_sells_mean_good,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[0,0],color=NOISE_GROUPS_PALETTE['good'],join=False,scale=2.2,markers='^',)
    sns.pointplot(data=pd.melt(df_sells_mean_bad,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[0,0],color=NOISE_GROUPS_PALETTE['bad'],join=False,scale=1.6,markers='s',)
    sns.pointplot(data=pd.melt(df_buys_mean_good,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[1,0],color=NOISE_GROUPS_PALETTE['good'],join=False,scale=2.2,markers='^',)
    sns.pointplot(data=pd.melt(df_buys_mean_bad,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[1,0],color=NOISE_GROUPS_PALETTE['bad'],join=False,scale=1.6,markers='s',)
    sns.pointplot(data=pd.melt(df_sells_max_good,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[0,1],color=NOISE_GROUPS_PALETTE['good'],join=False,scale=2.2,markers='^',)
    sns.pointplot(data=pd.melt(df_sells_max_bad,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[0,1],color=NOISE_GROUPS_PALETTE['bad'],join=False,scale=1.6,markers='s',)
    sns.pointplot(data=pd.melt(df_buys_max_good,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[1,1],color=NOISE_GROUPS_PALETTE['good'],join=False,scale=2.2,markers='^',)
    sns.pointplot(data=pd.melt(df_buys_max_bad,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[1,1],color=NOISE_GROUPS_PALETTE['bad'],join=False,scale=1.6,markers='s',)
    sns.pointplot(data=pd.melt(df_sells_min_good,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[0,2],color=NOISE_GROUPS_PALETTE['good'],join=False,scale=2.2,markers='^',)
    sns.pointplot(data=pd.melt(df_sells_min_bad,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[0,2],color=NOISE_GROUPS_PALETTE['bad'],join=False,scale=1.6,markers='s',)
    sns.pointplot(data=pd.melt(df_buys_min_good,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[1,2],color=NOISE_GROUPS_PALETTE['good'],join=False,scale=2.2,markers='^',)
    sns.pointplot(data=pd.melt(df_buys_min_bad,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[1,2],color=NOISE_GROUPS_PALETTE['bad'],join=False,scale=1.6,markers='s',)
    if show_variance:
        sns.pointplot(data=pd.melt(df_sells_var_good,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[0,4],color=NOISE_GROUPS_PALETTE['good'],join=False,scale=2.2,markers='^')
        sns.pointplot(data=pd.melt(df_sells_var_bad,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[0,4],color=NOISE_GROUPS_PALETTE['bad'],join=False,scale=1.6,markers='s')
        sns.pointplot(data=pd.melt(df_buys_var_good,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[1,4],color=NOISE_GROUPS_PALETTE['good'],join=False,scale=2.2,markers='^')
        sns.pointplot(data=pd.melt(df_buys_var_bad,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[1,4],color=NOISE_GROUPS_PALETTE['bad'],join=False,scale=1.6,markers='s')
    if number_of_saboteurs>0:
        warnings.filterwarnings( "ignore", module = "seaborn\..*" )#ignore color of "x" warning
        sns.pointplot(data=pd.melt(df_sells_mean_sab,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[0,0],color=NOISE_GROUPS_PALETTE['saboteur'],join=False,markers='x')
        sns.pointplot(data=pd.melt(df_buys_mean_sab,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[1,0],color=NOISE_GROUPS_PALETTE['saboteur'],join=False,markers='x')
        sns.pointplot(data=pd.melt(df_sells_max_sab,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[0,1],color=NOISE_GROUPS_PALETTE['saboteur'],join=False,markers='x')
        sns.pointplot(data=pd.melt(df_buys_max_sab,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[1,1],color=NOISE_GROUPS_PALETTE['saboteur'],join=False,markers='x')
        sns.pointplot(data=pd.melt(df_sells_min_sab,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[0,2],color=NOISE_GROUPS_PALETTE['saboteur'],join=False,markers='x')
        sns.pointplot(data=pd.melt(df_buys_min_sab,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[1,2],color=NOISE_GROUPS_PALETTE['saboteur'],join=False,markers='x')
        if show_variance:
            sns.pointplot(data=pd.melt(df_sells_var_sab,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[0,3],color=NOISE_GROUPS_PALETTE['saboteur'],join=False,markers='x')
            sns.pointplot(data=pd.melt(df_buys_var_sab,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[1,3],color=NOISE_GROUPS_PALETTE['saboteur'],join=False,markers='x')
        warnings.filterwarnings( "default", module = "seaborn\..*" )#ignore color of "x" warning
        # axs[0,0].set_xticklabels(['mean'])
        # axs[0,0].set_xlabel(None)
        # axs[0,0].set_ylabel('acceptance rate')
        # axs[0,0].set_title('sells mean')
        # axs[1,0].set_xticklabels(['mean'])
        # axs[1,0].set_xlabel(None)
        # axs[1,0].set_ylabel('acceptance rate')
        # axs[1,0].set_title('buys mean')

    # axs[0,0].set_xticklabels(['mean','median'])
    axs[0,0].set_xticklabels([None]*2)
    axs[0,0].set_xlabel(None)
    axs[0,0].set_ylabel('acceptance rate')
    axs[0,0].set_title('sells mean/median')
    axs[1,0].set_xticklabels(['mean','median'])
    axs[1,0].set_xlabel(None)
    axs[1,0].set_ylabel('acceptance rate')
    axs[1,0].set_title('buys mean/median')
    # axs[0,1].set_xticklabels(['mean','max'])
    axs[0,1].set_xticklabels([None]*2)
    axs[0,1].set_xlabel(None)
    # axs[0,1].set_ylabel('acceptance rate')
    axs[0,1].set_ylabel(None)
    axs[0,1].set_title('sells max')
    axs[1,1].set_xticklabels(['mean','max'])
    axs[1,1].set_xlabel(None)
    # axs[1,1].set_ylabel('acceptance rate')
    axs[1,1].set_ylabel(None)
    axs[1,1].set_title('buys max')
    # axs[0,2].set_xticklabels(['mean','min'])
    axs[0,2].set_xticklabels([None]*2)
    axs[0,2].set_xlabel(None)
    # axs[0,2].set_ylabel('acceptance rate')
    axs[0,2].set_ylabel(None)
    axs[0,2].set_title('sells min')
    axs[1,2].set_xticklabels(['mean','min'])
    axs[1,2].set_xlabel(None)
    # axs[1,2].set_ylabel('acceptance rate')
    axs[1,2].set_ylabel(None)
    axs[1,2].set_title('buys min')

    sns.pointplot(data=pd.melt(df_sells_good_ratio,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[0,3],color=NOISE_GROUPS_PALETTE['good'],join=False,scale=2.2,markers='^',)
    sns.pointplot(data=pd.melt(df_buys_good_ratio,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[1,3],color=NOISE_GROUPS_PALETTE['good'],join=False,scale=2.2,markers='^')
    sns.pointplot(data=pd.melt(df_sells_bad_ratio,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[0,3],color=NOISE_GROUPS_PALETTE['bad'],join=False,scale=1.6,markers='s')
    sns.pointplot(data=pd.melt(df_buys_bad_ratio,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[1,3],color=NOISE_GROUPS_PALETTE['bad'],join=False,scale=1.6,markers='s')
    if number_of_saboteurs>0:
        warnings.filterwarnings( "ignore", module = "seaborn\..*" )#ignore color of "x" warning
        sns.pointplot(data=pd.melt(df_sells_sab_ratio,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[0,3],color=NOISE_GROUPS_PALETTE['saboteur'],join=False,markers='x')
        sns.pointplot(data=pd.melt(df_buys_sab_ratio,id_vars=['plot_order']),x='plot_order',y='value',ax=axs[1,3],color=NOISE_GROUPS_PALETTE['saboteur'],join=False,markers='x')
        warnings.filterwarnings( "default", module = "seaborn\..*" )#ignore color of "x" warning
    axs[0,3].set_xticklabels([None])
    axs[0,3].set_xlabel(None)
    axs[0,3].set_ylabel(None)
    axs[0,3].set_title('sells ratio over total')
    axs[1,3].set_xlabel(None)
    axs[1,3].set_ylabel(None)
    axs[1,3].set_xticklabels([None])
    axs[1,3].set_title('buys ratio over total')

    if show_variance:
        # axs[0,4].set_xticklabels(['max','mean','min'])
        axs[0,4].set_xticklabels([None]*3)
        axs[0,4].set_xlabel(None)
        # axs[0,4].set_ylabel('acceptance rate')
        axs[0,4].set_ylabel(None)
        axs[0,4].set_title('sells variance')
        axs[1,4].set_xticklabels(['max','mean','min'])
        axs[1,4].set_xlabel(None)
        # axs[0,4].set_ylabel('acceptance rate')
        axs[1,4].set_ylabel(None)
        axs[1,4].set_title('buys variance')
        # axs[0,3].set_xticklabels(['max','mean','min'])
        # axs[0,3].set_xticklabels([None]*3)
        # axs[0,3].set_xlabel(None)
        # # axs[0,3].set_ylabel('acceptance rate')
        # axs[0,3].set_ylabel(None)
        # axs[0,3].set_title('sells variance')
        # axs[1,3].set_xticklabels(['max','mean','min'])
        # axs[1,3].set_xlabel(None)
        # # axs[1,3].set_ylabel('acceptance rate')
        # axs[1,3].set_ylabel(None)
        # axs[1,3].set_title('buys variance')
    [axs[i,j].yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0 if j!=4 else 3)) for i in range(2) for j in range(5 if show_variance else 4)]
    # [axs[i,j].yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0 if j!=3 else 2)) for i in range(2) for j in range(4 if show_variance else 3)]
    [ax.set_ylim(bottom=-3,top=103) for ax in axs.flatten()]
    if not multi_plot and not save_plot:plt.show()
    elif save_plot:
        plt.savefig(f"{save_folder}/{save_name}_buys_sells.png",dpi=300)
        plt.close()


def run_outlier(filename:str,WHIS=1.5):
    ''' detect outliers in a run (experiment)
    :param WHIS: whisker length for boxplot_stats

    :return: outlier amount, and agent,values dictionary
    '''
    df=dataframe_from_csv(filename,experiment_part="df")
    #OUTLIYING AGENT DETECTION AT DIFFERENT RUN-LEVEL
    dft=df.transpose()
    outliers=[]
    for run in dft.columns.to_list():
        outliers.append([x for stat in boxplot_stats(dft[run],whis=WHIS)
                            for x in stat['fliers'] ])
    del dft
    outl_agents={i:[] for i in df}
    for run_ol in outliers:
        for ol in run_ol:
            for agent in df:
                if df[agent].isin([ol]).any():
                    outl_agents[agent].append(ol)
                    break
    total_outliers=sum([len(outl_agents[agent]) for agent in outl_agents])
    # for run,ol in enumerate(outliers):
    #     if ol!=[]: print(f"run {run} ({len(outliers[run])}): {outliers[run]}")
    # for agent in outl_agents:
    #     if outl_agents[agent]!=[]: print(f"agent {agent} ({len(outl_agents[agent])}): {outl_agents[agent]}")
    # print("total outliers:",total_outliers)
    return outl_agents,total_outliers


#####################################################################################
# -----------------------EXPERIMENTS PLOTTING FUNCTIONS---------------------------------- #
def behaviours_buyers_sellers_groups(
                                data_folder,
                                experiment="",
                                # auto_xlabels=True,
                                n_robots=25,
                                n_honests=[25,24,22,20,17],
                                equally_sized_honest_groups=False,
                                lie_angles=[],
                                behaviours=[],
                                behavior_params_experiments=dict(),
                                combine_stategies=["waa"],
                                payment_systems=["P","NP"],
                                reputation_stake_list=[True,False],
                                noise_type_list=["uniform"],
                                noise_mu_list=[0.051],
                                noise_range_list=[0.1],
                                saboteur_performance_list=["avg","perf"],
                                # compare_with_reference=False,
                                # compare_best_of=False,
                                # compare_best_of_only=False,
                                separate_groups:bool=False,
                                show_variance:bool=False,
                                multi_plot=True,
                                save_plot=False,
                                save_folder="",
                                save_name="",):
    '''
    Plots the ration of buyers and sellers for each noise group

    The funciton will automatically fetch data from the data_folder and retrieve the
    experiment. Moreover, only a subset of experiment ticks can be specified

    :param data_folder: folder where the data is stored.

    :param experiment: experiment  subfolder to choose the data from.

    :param performance_metric: metric to plot. Permitted values are:
            "wealth", "wealth_evolution";
            "rewards", "rewards_evolution".

    :param n_robots: number of robots in the experiment; default: 25.

    :param n_honests: list of honest robots to retrieve experiments.

    :param equally_sized_honest_groups: if True, the honest robots are divided in
            equally sized groups even for perfect saboteurs (as in the average sab. case).

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
    # if compare_best_of_only:compare_best_of=True
    if multi_plot or save_plot:fig_count=0

    for behavior_initials in behaviours:
    # for n_honest in n_honests:
        # lie_angle=0 if n_honest==n_robots else 90
        # for noise_type in noise_type_list:
            for saboteur_performance in saboteur_performance_list:
                for noise_mu in noise_mu_list:
                    for noise_range in noise_range_list:
                        noise_params_values=[noise_mu,noise_range,saboteur_performance]
                        for payment_system in payment_systems:
                            for reputation_stake in reputation_stake_list:
                                if reputation_stake and payment_system=="NP":continue
                                for n_honest in n_honests:
                                    for lie_angle in lie_angles:
                                        if (lie_angle!=0 and n_honest==n_robots) or\
                                                (lie_angle==0 and n_honest!=n_robots):
                                            continue
                                    # for behavior_initials in behaviours:
                                        if (behavior_initials=="s" or behavior_initials=="n" or behavior_initials=="b") \
                                                and (reputation_stake or payment_system=='P') or \
                                                (behavior_initials=="r" or behavior_initials=="t" or behavior_initials=="c") \
                                                and (not reputation_stake or payment_system=='NP'):   
                                            continue
                                        for combine_stategy_initials in combine_stategies:
                                            behav_save_folder=join(save_folder,experiment,SUB_FOLDERS_DICT[behavior_initials])
                                            if save_plot and not os.path.exists(behav_save_folder):
                                                os.makedirs(join(behav_save_folder),exist_ok=True)
                                            for behavior_params_values in behavior_params_experiments[behavior_initials]:
                                                f=filename_from_params(n_honest,behavior_initials,
                                                                        combine_stategy_initials,
                                                                        payment_system,
                                                                        reputation_stake,
                                                                        lie_angle,
                                                                        behavior_params_values,
                                                                        "uniform",noise_params_values)
                                                # f=join(data_folder,experiment,SUB_FOLDERS_DICT[behavior_initials],\
                                                # performance_folder,f)+(".csv" if not f.endswith(".csv") else "")
                                                if not f.endswith(".csv"):f+=".csv"
                                                if not (CONFIG_FILE.PRUNE_FILENAMES  and \
                                                        ((CONFIG_FILE.PRUNE_NOT_BEST and is_best_param_combination(f)) or \
                                                        (not CONFIG_FILE.PRUNE_NOT_BEST and not is_bad_param_combination(f))) or \
                                                    not CONFIG_FILE.PRUNE_FILENAMES):
                                                    continue

                                                if save_plot:
                                                    # save_name=f"{n_honest}_{behavior_initials}_{payment_system}_{repu_stake}_{lie_angle}_{noise_mu}_{noise_range}_{saboteur_performance}"
                                                    save_name=f.split("/")[-1].split(".csv")[0]

                                                F=join(data_folder,experiment,SUB_FOLDERS_DICT[behavior_initials],'rewards',f)
                                                if not os.path.exists(F):
                                                    print(f"file {F} not found")
                                                    continue
                                                buyers_sellers_groups(
                                                                    filename=f,
                                                                    data_folder_and_subfolder=join(data_folder,experiment,SUB_FOLDERS_DICT[behavior_initials]),
                                                                    number_of_robots=n_robots,
                                                                    equally_sized_honest_groups=equally_sized_honest_groups,
                                                                    multi_plot=multi_plot,
                                                                    separate_groups=False,
                                                                    save_plot=save_plot,
                                                                    save_folder=behav_save_folder,
                                                                    save_name=save_name,
                                                                    show_variance=show_variance,
                                                                    )

                                                if multi_plot or save_plot:fig_count+=1

    if multi_plot:plt.show()
    elif save_plot:print(f"saved {fig_count} figures in {join(save_folder,experiment)}")


def behaviors_market_analysis(
                            data_folder,
                            experiment="",
                            performance_metric="",
                            analysis_type="",
                            pair_plot=True,
                            fill_between=False,
                            # auto_xlabels=True,
                            n_robots=25,
                            n_honests=[25,24,22,20,17],
                            equally_sized_honest_groups=False,
                            lie_angles=[],
                            behaviours=[],
                            behavior_params_experiments=dict(),
                            combine_stategies=["waa"],
                            payment_systems=["P","NP"],
                            reputation_stake_list=[True,False],
                            noise_types=["uniform"],
                            noise_mu_list=[0.051],
                            noise_range_list=[0.1],
                            saboteur_performance_list=["avg","perf"],
                            # compare_with_reference=False,
                            # compare_best_of=False,
                            # compare_best_of_only=False,
                            multi_plot=True,
                            save_plot=False,
                            save_folder="",
                            save_name="",
                            ):
    '''
    This function plots evolution of wither one or both reward, wealth(includes).
    Time (simultion ticks) is showed on the x axis, metric for all noise groups on the y axis.

    The funciton will automatically fetch data from the data_folder and retrieve the
    experiment. Moreover, only a subset of experiment ticks can be specified

    :param data_folder: folder where the data is stored.

    :param experiment: experiment  subfolder to choose the data from.

    :TODO param experiment_part: initial and final ticks to plot. If empty, all ticks are plotted;
            default: [].

    :param performance_metric: metric to plot. Permitted values are:
            "wealth", "wealth_evolution";
            "rewards", "rewards_evolution".

    :param analysis_type: type of analysis to perform. Permitted values are:
        -"evolution", "market_evolution", : plots the evolution of the metric in the market
        -"gini", "lorenz", "inequality": plots the inequality of the metric in the market
        -"distribution", "wealth_distribution": plots the distribution of the metric in the market

    :param n_robots: number of robots in the experiment; default: 25.

    :param n_honests: list of honest robots to retrieve experiments.

    :param equally_sized_honest_groups: if True, the honest robots are divided in
            equally sized groups even for perfect saboteurs (as in the average sab. case).

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
    #TODO pass kwargs to market_function
    if "evolution" in analysis_type:
        market_function=market_metric_evolution
        save_folder=save_folder.replace("ANALYSIS_FOLDER","market_values")
    elif "gini" in analysis_type or "lorenz" in analysis_type or "inequality" in analysis_type:
        market_function=market_lorenz_gini
        save_folder=save_folder.replace("ANALYSIS_FOLDER","gini_index")
    elif "distribution" in analysis_type:
        market_function=market_wealth_distribution
        save_folder=save_folder.replace("ANALYSIS_FOLDER","wealth_distribution")

    # if compare_best_of_only:compare_best_of=True

    if multi_plot or save_plot:fig_count=0

    # if 'reward' in performance_metric:
    #     # performance_folder="rewards_evolution"
    #     if pair_plot:secondary_performance="wealth_evolution"
    # elif 'wealth' in performance_metric:
    #     # performance_folder="wealth_evolution"
    #     if pair_plot:secondary_performance="rewards_evolution"

    for behavior_initials in behaviours:
    # for n_honest in n_honests:
        # lie_angle=0 if n_honest==n_robots else 90
        for noise_type in noise_types:
            for saboteur_performance in saboteur_performance_list:
                for noise_mu in noise_mu_list:
                    for noise_range in noise_range_list:
                        noise_params_values=[noise_mu,noise_range,saboteur_performance]
                        for payment_system in payment_systems:
                            for reputation_stake in reputation_stake_list:
                                if reputation_stake and payment_system=="NP":continue
                                for n_honest in n_honests:
                                    for lie_angle in lie_angles:
                                        if (lie_angle!=0 and n_honest==n_robots) or\
                                                (lie_angle==0 and n_honest!=n_robots):
                                            continue
                                        # for behavior_initials in behaviours:
                                        if ((behavior_initials=="s" or behavior_initials=="n" or behavior_initials=="b") \
                                                and (reputation_stake or payment_system=='P')) or \
                                                ((behavior_initials=='t' or behavior_initials=='r' or behavior_initials=='c') \
                                                and (payment_system=='NP')):
                                            continue
                                        for combine_stategy_initials in combine_stategies:
                                            behav_save_folder=join(save_folder,experiment,SUB_FOLDERS_DICT[behavior_initials])
                                            if save_plot and not os.path.exists(behav_save_folder):
                                                os.makedirs(join(behav_save_folder),exist_ok=True)
                                            for behavior_params_values in behavior_params_experiments[behavior_initials]:
                                                f=filename_from_params(n_honest,behavior_initials,
                                                                        combine_stategy_initials,
                                                                        payment_system,
                                                                        reputation_stake,
                                                                        lie_angle,
                                                                        behavior_params_values,
                                                                        "uniform",noise_params_values)
                                                # f=join(data_folder,experiment,SUB_FOLDERS_DICT[behavior_initials],\
                                                # performance_folder,f)+(".csv" if not f.endswith(".csv") else "")
                                                if not f.endswith(".csv"):f+=".csv"
                                                if not (CONFIG_FILE.PRUNE_FILENAMES  and \
                                                        ((CONFIG_FILE.PRUNE_NOT_BEST and is_best_param_combination(f)) or \
                                                        (not CONFIG_FILE.PRUNE_NOT_BEST and not is_bad_param_combination(f))) or \
                                                    not CONFIG_FILE.PRUNE_FILENAMES):
                                                    continue

                                                if save_plot:
                                                    # save_name=f"{n_honest}_{behavior_initials}_{payment_system}_{repu_stake}_
                                                    #               {lie_angle}_{noise_mu}_{noise_range}_{saboteur_performance}"
                                                    save_name=f.split("/")[-1].split(".csv")[0]
                                                
                                                F=join(data_folder,experiment,SUB_FOLDERS_DICT[behavior_initials],'rewards',f)
                                                if not os.path.exists(F):
                                                    print(f"file {F} not found")
                                                    continue

                                                if behavior_initials=="s" or behavior_initials=="n" or behavior_initials=="b":
                                                    performance_metric="reward"
                                                    pair_plot=False

                                                market_function(
                                                        filename=f,
                                                        data_folder_and_subfolder=join(data_folder,experiment,SUB_FOLDERS_DICT[behavior_initials]),
                                                        metric=performance_metric,
                                                        number_of_robots=n_robots,
                                                        equally_sized_honest_groups=equally_sized_honest_groups,
                                                        multi_plot=multi_plot,
                                                        pair_plot=pair_plot,
                                                        fill_between=fill_between,
                                                        save_plot=save_plot,
                                                        save_folder=behav_save_folder,
                                                        save_name=save_name
                                                        )

                                                if multi_plot or save_plot:fig_count+=1

    if multi_plot:plt.show()
    elif save_plot:print(f"saved {fig_count} figures in {join(save_folder,experiment)}")


def compare_behaviors_performance(
                                        data_folder,
                                        experiment="",
                                        experiment_part="whole",
                                        performance_metric="",
                                        compare_evolution=False,
                                        pair_plot=False,
                                        short_x_labels=False,
                                        transparent_boxes=False,
                                        quality_index="",
                                        multi_quality=False,
                                        show_dishonests=False,
                                        auto_xlabels=True,
                                        n_robots=25,
                                        n_honests=[25,24,22,],
                                        equally_sized_honest_groups=False,
                                        lie_angles=[0,90],
                                        behaviours=[],
                                        behavior_params_experiments=dict(),
                                        combine_stategies=["waa"],
                                        payment_systems=["P","NP"],
                                        reputation_stakes=[True,False],
                                        noise_type_list=["uniform"],
                                        noise_mu_list=[0.051],
                                        noise_range_list=[0.1],
                                        saboteur_performance_list=["avg","perf"],
                                        compare_with_reference=False,
                                        compare_best_of=False,
                                        compare_best_of_only=False,
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

    :param equally_sized_honest_groups: if True, the honest robots are divided in
            equally sized groups even for perfect saboteurs (as in the average sab. case).

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
    #TODO kwargs for performance function
    # if compare_evolution:
    #     performance_function=performance_evolution
    # else:
    #     performance_function=performance_with_quality

    if compare_best_of_only:compare_best_of=True
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

    if transparent_boxes:
        import matplotlib#to find boxes element

    for n_honest in n_honests:
        for lie_angle in lie_angles:
            if (lie_angle!=0 and n_honest==n_robots) or\
                    (lie_angle==0 and n_honest!=n_robots):
                continue
            for noise_type in noise_type_list:
                for saboteur_performance in saboteur_performance_list:
                    for noise_mu in noise_mu_list:
                        for noise_range in noise_range_list:
                            noise_params_values=[noise_mu,noise_range,saboteur_performance]

                            if compare_best_of: best_list=[];best_labels=[]
                            for payment_system in payment_systems:
                                for reputation_stake in reputation_stakes:
                                    if reputation_stake and payment_system=="NP":
                                        continue
                                    for behavior_initials in behaviours:
                                        if (behavior_initials=='b' and reputation_stake) or\
                                                behavior_initials=='s' or behavior_initials=='n':
                                            continue
                                        for combine_stategy_initials in combine_stategies:
                                            if save_plot:
                                                behav_save_folder=join(save_folder,experiment,performance_metric,SUB_FOLDERS_DICT[behavior_initials])
                                                if not os.path.exists(behav_save_folder):os.makedirs(behav_save_folder,exist_ok=True)
                                            if compare_with_reference:
                                                filenames=[
                                                    filename_from_params(n_honest,"n", "waa",
                                                                        "NP","NRS",lie_angle,
                                                                        [],
                                                                        noise_type,noise_params_values),
                                                    # filename_from_params(n_honest,"n", "waa",
                                                    #                     "NP","NRS",lie_angle,
                                                    #                     [],
                                                    #                     noise_type,noise_params_values),
                                                    # filename_from_params(n_honest,"s", "waa",
                                                    #                     "NP","NRS",lie_angle,
                                                    #                     [0.25],
                                                    #                     noise_type,noise_params_values),
                                                    filename_from_params(n_honest,"s", "waa",
                                                                        "NP","NRS",lie_angle,
                                                                        [0.25],
                                                                        noise_type,noise_params_values),
                                                    ]
                                                BASIC_BEHAV_LEN=len(filenames)
                                                filenames=[join(data_folder,experiment,SUB_FOLDERS_DICT[b_i],\
                                                    performance_folder,f)+(".csv" if not f.endswith(".csv") else "")\
                                                        for f,b_i in zip(filenames,(['s'] if BASIC_BEHAV_LEN==1 else ['n','s'] if BASIC_BEHAV_LEN==2 else ['n','n','s','s']))]

                                                if not auto_xlabels:
                                                    if BASIC_BEHAV_LEN==4: x_labels=["Naive\nno penalisation","Naive\npenalisation","Sceptical\nno penalisation","Sceptical\npenalisation"]
                                                    elif BASIC_BEHAV_LEN==2: x_labels=["Naive\nno penalisation","Sceptical\nno penalisation"]
                                                    elif BASIC_BEHAV_LEN==1: x_labels=["Sceptical\nno penalisation"]
                                                    if short_x_labels:
                                                        if BASIC_BEHAV_LEN==4: x_labels=["n\nNP, NRS","n\nP, NRS","s\nNP, NRS","s\nP, NRS"]
                                                        elif BASIC_BEHAV_LEN==2: x_labels=["n\nNP, NRS","s\nNP, NRS"]
                                                        elif BASIC_BEHAV_LEN==1: x_labels=["s\nNP, NRS"]
                                                else: x_labels=[]
                                            else:
                                                filenames=[]
                                                x_labels=[]
                                                BASIC_BEHAV_LEN=0
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
                                                            repustake_text=f"{'' if reputation_stake else 'N'}RS"
                                                        x_label=f"{behav_label}\n"\
                                                        f"{behavior_params_text}"\
                                                        f"{penalisation_text}, {repustake_text}"
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
                                            # if reputation_stake:title+=",   \nwith Staking based on reputation"
                                            repu_stake=f"{'' if reputation_stake else 'N'}RS"
                                            save_name=f"{n_honest}_{behavior_initials}_{payment_system}_{repu_stake}_{lie_angle}_{noise_mu}_{noise_range}_{saboteur_performance}"

                                            if not len(filenames)>BASIC_BEHAV_LEN:continue

                                            if pair_plot:
                                                secondary_filenames=[f.replace(performance_folder,secondary_performance_folder) for f in filenames]
                                                filenames=[filenames,secondary_filenames]
                                            if not compare_best_of_only:
                                                if compare_evolution:
                                                    performance_evolution(
                                                                    filename=f,#[x]
                                                                    # data_folder_and_subfolder=join(data_folder,experiment,SUB_FOLDERS_DICT[behavior_initials]),
                                                                    # metric=performance_metric,
                                                                    number_of_robots=n_robots,
                                                                    equally_sized_honest_groups=equally_sized_honest_groups,
                                                                    multi_plot=multi_plot,
                                                                    pair_plot=pair_plot,
                                                                    save_plot=save_plot,
                                                                    save_folder=behav_save_folder,
                                                                    save_name=save_name
                                                                    )
                                                else:
                                                    try:
                                                        performance_with_quality(
                                                                            filenames,
                                                                            experiment_part=experiment_part,
                                                                            performance_index=performance_metric,
                                                                            equally_sized_honest_groups=equally_sized_honest_groups,
                                                                            pair_plot=pair_plot,
                                                                            quality_index=quality_index,
                                                                            multi_quality=multi_quality,
                                                                            title=title,
                                                                            x_labels=x_labels,
                                                                            transparent_boxes=transparent_boxes,
                                                                            show_dishonests=show_dishonests if n_honest<n_robots else False,
                                                                            multi_plot=multi_plot,
                                                                            save_plot=save_plot,
                                                                            save_folder=behav_save_folder if save_plot else "",
                                                                            save_name=save_name,
                                                                            )
                                                    except Exception as e:
                                                        filenames_not_existant=[f for f in filenames if os.path.isfile(f)]
                                                        print(f"Error {e}\n in non existant files:\n{filenames_not_existant}")
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
                                # if reputation_stake:title+=",   \nwith Staking based on reputation"

                                if compare_evolution:
                                    performance_evolution(
                                                        best_list,
                                                        # data_folder_and_subfolder=join(data_folder,experiment,SUB_FOLDERS_DICT[behavior_initials]),
                                                        # metric=performance_metric,
                                                        number_of_robots=n_robots,
                                                        equally_sized_honest_groups=equally_sized_honest_groups,
                                                        multi_plot=multi_plot,
                                                        pair_plot=pair_plot,
                                                        save_plot=save_plot,
                                                        save_folder=join(save_folder,experiment,performance_metric) \
                                                            if save_plot else "",
                                                        save_name=best_save_name,
                                                        )
                                else:
                                    performance_with_quality(
                                                            best_list,
                                                            experiment_part=experiment_part,
                                                            performance_index=performance_metric,
                                                            equally_sized_honest_groups=equally_sized_honest_groups,
                                                            pair_plot=pair_plot,
                                                            quality_index=quality_index,
                                                            multi_quality=multi_quality,
                                                            title=title,
                                                            x_labels=best_labels,
                                                            transparent_boxes=transparent_boxes,
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


def comparison_bimodal_uniform_noise(
                                        data_folder,
                                        experiment="",
                                        metric="",
                                        n_robots=25,
                                        n_honests=[25,24,22,],
                                        equally_sized_honest_groups=False,
                                        lie_angles=[],
                                        behaviors=["n","s","r","Nv","t","w"],
                                        behavior_params_experiments=dict(),
                                        combine_strategies=["waa"],
                                        payment_systems=["P","NP"],
                                        reputation_stakes=["RS","NRS"],
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
    '''
    TODO comparison_bimodal_uniform_noise docstring
    :param equally_sized_honest_groups: if True, the honest robots are divided in
            equally sized groups even for perfect saboteurs (as in the average sab. case).
    '''
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
                        for reputation_stake in reputation_stakes:
                            for lie_angle in lie_angles:
                                if (lie_angle!=0 and n_honest==n_robots) or\
                                        (lie_angle==0 and n_honest!=n_robots):
                                    continue
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
                                noise_metric_analysis(filenames,
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


##############################################################################################################
##############################################################################################################
#TODO: create this as a summary from config generation / running
#TODO add lie_angle selection instead of only 0, 90
#TODO autofetch from given folder BUT CAN CHOOSE WHAT TO INLCUDE IF SPECIFIED
#       cycle to create a vector of specified
#       fetch all filenames from folder
#       if specified!=[]: filter filenames if fetch[i] in specified
#       NOTE MUST SPECIFY HOW BO BUILD THE COMPARISON VECTOR (INTRA/EXTRA BEHAV)

if __name__ == '__main__':
    data_folder=CONFIG_FILE.DATA_DIR
    save_plot:bool=1
    multi_plot:bool=1

    # experiment="a_IM_HEU/IM_7_1_1_UNBIASED_DEFAULT_HEURISTIC"
    experiment="IM_7_1_1_NODEF_NORM_50K"
    experiments=[
                "IM_7_1_1_DEF_NORM_50K",
                "IM_7_1_1_NODEF_NORM_50K",
                ]   
    experiment_part="last.33"
    # experiment_part="whole"
    ######################################################
    number_of_robots=25
    number_of_honests=[
                        # 25,
                        # 24,
                        # 22,
                        20,
                        # 23,
                        # 17
                        ]
    lie_angles=[
                # 0,
                # 25,
                90
                ]
    saboteur_performances=[
                            "avg",
                            "perf"
                        ]
    equally_sized_honest_groups=True
    behaviors=[
                # 'n',
                # 's',
                # 'b',
                'c',
                'r',
                't',
                # 'Nv',
                # 'h',
                # 'hs',
                ]
    ######################################################
    payment_systems=[
                        "P",
                        "NP"
                    ]
    reputation_stakes=[
                        True,
                        False
                    ]
    ######################################################
    COMPARE_PERFORMANCES:bool=0
    performance_metric_compare_performances="items"
    # performance_metric_compare_performances="rewards"
    quality_metric_compare_performances="transactionsS"
    ######################################################
    MARKET_EVOLUTION:bool=0
    performance_metric_market_evolution="wealth"

    WEALTH_INEQUALITY_ANALYSIS:bool=1
    performance_metric_inequality_analysis="wealth"

    WEALTH_DISTRIBUTION_ANALYSIS:bool=1
    performance_metric_wealth_distribution="wealth"

    DO_MARKET_ANALYSIS=[MARKET_EVOLUTION,WEALTH_INEQUALITY_ANALYSIS,WEALTH_DISTRIBUTION_ANALYSIS]
    TYPES_OF_ANALYSIS=["evolution","gini","distribution"]
    MARKET_PERFORMANCE_METRICS=[performance_metric_market_evolution,
                    performance_metric_inequality_analysis,performance_metric_wealth_distribution]
    ######################################################
    BUYERS_SELLERS_GROUPS:bool=1
    ######################################################
    #BUG comparison_bimodal_uniform_noise():filename_from_params(), missing argument: 'noise_params_values'
    NOISE_COMPARISON:bool=0
    performance_metric_noise_comparison="reward"

    NOISE_LEVELS:bool=0
    ######################################################
    FIND_SEEDS:bool=0
    performance_metric_find_seeds="items_collected"
    ######################################################

    for experiment in experiments:
        if COMPARE_PERFORMANCES:
            compare_behaviors_performance(
                                            data_folder=data_folder,
                                            experiment=experiment,
                                            experiment_part=experiment_part,
                                            performance_metric=performance_metric_compare_performances,
                                            pair_plot=0,
                                            short_x_labels=True,
                                            transparent_boxes=False,
                                            quality_index=quality_metric_compare_performances,
                                            multi_quality=True,
                                            show_dishonests=True,
                                            auto_xlabels=False,
                                            n_honests=number_of_honests,
                                            lie_angles=lie_angles,
                                            behaviours=behaviors,#to compare w/ n+NP,n+P,s+NP,s+P
                                            behavior_params_experiments=BEHAV_PARAMS_COMBINATIONS,
                                            payment_systems=payment_systems,
                                            reputation_stakes=reputation_stakes,
                                            saboteur_performance_list=saboteur_performances,
                                            compare_with_reference=1,
                                            compare_best_of=0,
                                            compare_best_of_only=0,
                                            multi_plot=multi_plot,
                                            save_folder=join(CONFIG_FILE.PLOT_DIR,"behav_comparison"),
                                            save_plot=save_plot
                                        )

        [behaviors_market_analysis(
                                data_folder=data_folder,
                                experiment=experiment,
                                performance_metric=analysis_metric,    
                                analysis_type=analysis_type,
                                pair_plot=1,
                                fill_between=True,
                                # auto_xlabels=True,
                                n_honests=number_of_honests,
                                equally_sized_honest_groups=equally_sized_honest_groups,
                                lie_angles=lie_angles,
                                behaviours=behaviors,
                                behavior_params_experiments=BEHAV_PARAMS_COMBINATIONS,
                                payment_systems=payment_systems,
                                reputation_stake_list=reputation_stakes,
                                saboteur_performance_list=saboteur_performances,
                                # compare_with_reference=False,
                                # compare_best_of=False,
                                # compare_best_of_only=False,
                                multi_plot=multi_plot,
                                save_folder=join(CONFIG_FILE.PLOT_DIR,"ANALYSIS_FOLDER"),
                                save_plot=save_plot
                                )
            for DO_ANALYSIS, analysis_type,analysis_metric in zip(DO_MARKET_ANALYSIS,TYPES_OF_ANALYSIS,MARKET_PERFORMANCE_METRICS)
            if DO_ANALYSIS
        ]        

        if BUYERS_SELLERS_GROUPS:
            behaviours_buyers_sellers_groups(
                                data_folder=data_folder,
                                experiment=experiment,
                                n_honests=number_of_honests,
                                equally_sized_honest_groups=equally_sized_honest_groups,
                                lie_angles=lie_angles,
                                behaviours=behaviors,
                                behavior_params_experiments=BEHAV_PARAMS_COMBINATIONS,
                                payment_systems=payment_systems,
                                reputation_stake_list=reputation_stakes,
                                saboteur_performance_list=saboteur_performances,
                                separate_groups=False,
                                # show_variance=True,
                                # compare_with_reference=False,
                                # compare_best_of=False,
                                # compare_best_of_only=False,
                                multi_plot=multi_plot,
                                save_folder=join(CONFIG_FILE.PLOT_DIR,"buys_sells_groups"),
                                save_plot=save_plot
                                    )

        if NOISE_COMPARISON:
            comparison_bimodal_uniform_noise(
                                        data_folder=data_folder,
                                        experiment=experiment,
                                        metric=performance_metric_noise_comparison,
                                        n_honests=number_of_honests,
                                        lie_angles=lie_angles,
                                        behaviors=behaviors,
                                        behavior_params_experiments=BEHAV_PARAMS_COMBINATIONS,
                                        multi_plot=multi_plot,
                                        save_folder=join(CONFIG_FILE.PLOT_DIR,"noise_comparison"),
                                        save_plot=save_plot
                                        )
            
        if NOISE_LEVELS:
            [noise_level(
                            number_agents=number_of_robots,
                            number_saboteurs=number_of_robots-n_h,
                            noise_average=0.051,
                            noise_range=0.1,
                            saboteurs_noise="perfect" if s_p=="perf" else "average",
                            )
                for n_h in number_of_honests
                for s_p in saboteur_performances
            ]

        if FIND_SEEDS:
            find_best_worst_seeds(filenames=[],
                            data_folder=data_folder,
                            metric=performance_metric_find_seeds,
                            base_seed=5684436,
                            amount_to_find=3,
                        )
