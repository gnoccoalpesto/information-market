import re
import os
from os.path import join, isfile,exists
import argparse
from random import gauss, random
import time

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick # to plot percentage on axis for matplotlib
from  matplotlib.ticker import FuncFormatter #to force axis to have integer ticks
import seaborn as sns
import scipy.stats as stats

import config as CONFIG_FILE
from model.environment import generate_uniform_noise_list
from model.behavior import  BEHAVIORS_NAME_DICT, SUB_FOLDERS_DICT, PARAMS_NAME_DICT, BEHAVIOR_PARAMS_DICT
from info_market import filename_from_params, params_from_filename,is_bad_param_combination, is_best_param_combination


# BEHAVIOUR_PALETTE={'n':"#000000",
#                     'Nn':,
#                     's':,
#                     'Ns':,
#                     'r':,
#                     'v':,
#                     'Nv':,
#                     't':,
#                     'w':}


BEHAV_PARAMS_COMBINATIONS={"n":[[]],
                                "s":[[0.25]],
                                "r":[[0.3],[0.5]],
                                "Nv":[["allavg",0.3,0.25,"exponential"],
                                    ["allavg",0.5,0.25,"exponential"],
                                    ["allavg",0.8,0.25,"exponential"],
                                    ["allavg",0.3,0.25,"ratio"],
                                    ["allavg",0.5,0.25,"ratio"],
                                    ["allavg",0.8,0.25,"ratio"],
                                    ["allmax",0.3,0.25,"exponential"],
                                    ["allmax",0.5,0.25,"exponential"],
                                    ["allmax",0.8,0.25,"exponential"],
                                    ["allmax",0.3,0.25,"ratio"],
                                    ["allmax",0.5,0.25,"ratio"],
                                    ["allmax",0.8,0.25,"ratio"]],
                                "t":[["allavg",0.3],
                                    ["allavg",0.5],
                                    ["allavg",0.8],
                                    ["allmax",0.3],
                                    ["allmax",0.5],
                                    ["allmax",0.8]],
                                "w":[[]]
                                }

#------------------------------------------------------------------------------------------------
#---------------------------------------UTILITIES------------------------------------------------
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


def load_data_from_csv(filename,
                        data_folder_and_subfolder="",
                        metric="",
                        experiment_part="whole",
                        post_processing=None,
                        #TODO decorate_saboteurs=False,
                    ):
    '''
    returns the appropriate DataFrame, given the filename and the experiment part

    :param filename: the name of the file to load, must include the extension

    :param data_folder_and_subfolder: the folder where the data is stored, must include up to the metric

    :param metric: the metric to choose from.  Accepted values are:
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

    if experiment_part=="whole" or "transaction" in metric:
        if metric=="items": metric_folder="items_collected"
        elif "transaction" in metric:
            metric_folder="transactions"
            if metric[-1]=="A": filename=filename.split(".csv")[0]+"_attempted.csv"
            elif metric[-1]=="V": filename=filename.split(".csv")[0]+"_validated.csv"
            elif metric[-1]=="C": filename=filename.split(".csv")[0]+"_completed.csv"
            elif metric[-1]=="X": filename=filename.split(".csv")[0]+"_combined.csv"
            else: filename=filename.split(".csv")[0]+"_combined.csv"
        elif metric=="": metric_folder=""
        df=pd.read_csv(join(data_folder_and_subfolder,metric_folder,filename), header=None)

    elif "last" in experiment_part:
        #BUG not working with float: must automatically change for reward
        def string_list_to_array(string:str, element_type=int):
            return np.asarray([element_type(_) for _ in string.replace("[","").replace("]","").split(", ")])
            # return np.asarray(re.search("[0-9]+", string).group(0))
        if metric=="items": metric_folder="items_evolution"
        elif metric=="rewards": metric_folder="rewards_evolution"
        elif metric=="" and "evolution" in filename:
            splitted_filename=filename.split(".csv")[0].split("/")
            if data_folder_and_subfolder=="":
                data_folder_and_subfolder="/".join(splitted_filename[:-2])
            metric_folder="items_evolution" if "item" in filename else "rewards_evolution"
            filename=splitted_filename[-1]+".csv"

        n_last_part=float(re.findall(r"[-+]?(?:\d*\.*\d+)", experiment_part)[0])
        if n_last_part>=1: n_last_part/=100
        n_last_part=1-n_last_part

        df=pd.read_csv(join(data_folder_and_subfolder,metric_folder,filename))
        col_labels=df.columns.to_list()
        experiment_runs=df[col_labels[0]].unique()
        df_list=[]
        for run in experiment_runs:
            run_rows=df.loc[lambda df: df[col_labels[0]] == run].iloc[:,-1]
            last_run_row=string_list_to_array(run_rows.iloc[-1])
            start_last_part_run_row=string_list_to_array(run_rows.iloc[int(n_last_part*len(run_rows))])
            delta_run_rows=last_run_row-start_last_part_run_row
            df_list.append(delta_run_rows)
        df=pd.DataFrame(df_list)

    elif experiment_part=="steps":
        def string_list_to_array(string:str, element_type=int):
            return np.asarray([element_type(_) for _ in string.replace("[","").replace("]","").split(", ")])
        if metric=="items": metric_folder="items_evolution"
        elif metric=="rewards": metric_folder="rewards_evolution"

        df=pd.read_csv(join(data_folder_and_subfolder,metric_folder,filename))
        col_labels=df.columns.to_list()
        df_list=[]
        for _,row in df.iterrows():
            row_list=string_list_to_array(row[col_labels[-1]])
            new_row=[row[col_labels[0]],row[col_labels[1]],*row_list]
            df_list.append(new_row)
        new_col_labels=col_labels[:-1]+[f"{metric}_{robot_id}" for robot_id in range(len(row_list))]
        df=pd.DataFrame(df_list,columns=new_col_labels)

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
                                payment_systems=["P","NP"],
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
                    lie_angle=0 if n_honest==n_robots else 90

                    behavior_params_text=""
                    for v,p in zip(behavior_params_values,BEHAVIOR_PARAMS_DICT[behavior_initials]):
                        behavior_params_text+=f"{v} {PARAMS_NAME_DICT[p]},"
                    #TODO FORMAT OF filenames
                    filenames=[ filename_from_params(n_honest,
                                            behavior_initials,
                                            payment_system,
                                            lie_angle,
                                            behavior_params_values,
                                            RELEVANT_NOISE_TYPE,
                                            RELEVANT_NOISE_PARAMS)
                            ]
                    filenames=[data_folder+experiment+"/"+SUB_FOLDERS_DICT[behavior_initials]+"/"+metric+"/"+filename+".csv" for filename in filenames]
                    filenames_list.append(filenames)
    return filenames_list


#------------------------------------------------------------------------------------------------
#---------------------------------------STATISTICAL TESTS----------------------------------------
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
    in this shape /DATA_FOLDER/METRIC/FILENAME.csv
    """
    if amount_to_find<1:amount_to_find=1
    data_folder=f"{data_folder}{metric}/" if data_folder!="" else ""
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


#------------------------------------------------------------------------------------------------
#-----------------------------------BASE PLOTTING FUNCTIONS--------------------------------------
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
                        quality_index="transactions",#"reward"
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

    :param quality_index: the quality index to be plotted. Automatically fetced based on filenames.
            Required format: [quality_measure]-[quality_function]
        quality_measure: the quality measure to be plotted. Supported values:
         -"trans(actions)": will plot the ratio between a function of both completed and attempted transactions.
           If "trans(actions)C" is specified, will use combined/completed; otherwise attempted/completed.
          "reward(s)": will plot a function of the rewards
        quality_function: supported values: "sum", "mean", "median", "max", "min", "std". "median" by default.

    :param show_dishonests: toggle separate boxplot for dishonests agents performance. Default: True
    transactions: completed/attempted -> NARROW INTERVAL high naive, low sceptical, ranking in between
                 combined/completed -> LARGE INTERVAL low naive, medium sceptical, ranking, high variable scepticism
    '''
    BASE_BOX_WIDTH=16
    BASE_BOX_HEIGHT=7
    base_title="Performance of Reputation Systems"
    n_subplots=1
    fig, axs = plt.subplots(1, n_subplots, sharey=True)#squeeze=False)#solves non subscriptable error
    #BUG but causes error in case of saboteurs plot

    if not quality_index=="":
        try:
            quality_index, quality_function=quality_index.split("-")
        except ValueError:
            quality_function="median"
    if show_dishonests:
        honest_list=[]
        dishonest_list=[]
    else:
        performance_list=[]
    quality_list=[]

    if not x_labels:
        x_labels=[]
        auto_x_labels=True
    else:auto_x_labels=False

    for i,f in enumerate(filenames):
        if not f.endswith(".csv"):f+=".csv"
        splitted_filename=f.split('.csv')[0].split("/")
        df=load_data_from_csv(f,experiment_part=experiment_part)
        n_honest, honest_behavior, payment, _, behaviour_params, _=params_from_filename(f,compact_format=True)
        
        if auto_x_labels:
            behavior_params_text=""
            for v,p in zip(behaviour_params,BEHAVIOR_PARAMS_DICT[honest_behavior]):
                behavior_params_text+=f"{v} {p},\n"
            x_labels.append(f"{BEHAVIORS_NAME_DICT[honest_behavior]}\n"
            f"{behavior_params_text}"
            f"{'no ' if payment=='NP' else ''}penalis.")

        if show_dishonests:
            df_honest=df.iloc[:,:int(n_honest)]
            df_dishonest=df.iloc[:,int(n_honest):]
            df_honest['behavior']=BEHAVIORS_NAME_DICT[honest_behavior]
            df_dishonest['behavior']=BEHAVIORS_NAME_DICT[honest_behavior]
            df_honest['honesty']='honest'
            df_dishonest['honesty']='dishonest'
            df_honest['plot_order']=i
            df_dishonest['plot_order']=i
            honest_list.append(df_honest)
            dishonest_list.append(df_dishonest)
        else:
            df['behavior']=BEHAVIORS_NAME_DICT[honest_behavior]
            df['plot_order']=i
            performance_list.append(df)

        if not quality_index=="":
            if "trans" in quality_index:
                if "C" in quality_index:
                    numerator_quality="combined"
                else:
                    numerator_quality="attempted"
                denominator_quality="completed"
                fq1="/".join(splitted_filename[:-2]+["transactions"]+splitted_filename[-1:])+f"_{numerator_quality}.csv"
                fq2="/".join(splitted_filename[:-2]+["transactions"]+splitted_filename[-1:])+f"_{denominator_quality}.csv"
                df_quality1=load_data_from_csv(fq1,post_processing="all-"+quality_function)
                df_quality2=load_data_from_csv(fq2,post_processing="all-"+quality_function)
                df_quality=df_quality1/df_quality2

            elif "reward" in quality_index:
                fq="/".join(splitted_filename[:-2]+["rewards"]+splitted_filename[-1:])+".csv"
                df_quality=load_data_from_csv(fq,post_processing="all-"+quality_function)
            df_quality=pd.DataFrame(df_quality,columns=[quality_index])
            df_quality['behavior']=BEHAVIORS_NAME_DICT[honest_behavior]
            df_quality['plot_order']=i
            quality_list.append(df_quality)

    if show_dishonests:
        data_honest=pd.concat(honest_list)
        data_dishonest=pd.concat(dishonest_list)
    else:
        data_performance=pd.concat(performance_list)

    if show_dishonests:
        sns.boxplot(data=pd.melt(data_honest, id_vars=['behavior','honesty','plot_order']),
                        x='plot_order',y='value', hue='behavior',
                        linewidth=1, dodge=False,width=.5,palette="deep")#.set(xlabel=None,ylabel=None,xticklabels=[],xticks=[])
        sns.boxplot(data=pd.melt(data_dishonest, id_vars=['behavior','honesty','plot_order']),
                        x='plot_order',y='value', hue='behavior',#["red"]*len(filenames), #color="red" for red palette
                        linewidth=1.65, dodge=True, saturation=0.85, width=0.5, ax=axs)#.set(ylabel=performance_label)
        # performance_max=max(max(data_dishonest.iloc[:,int(n_honest):].apply(np.max)),max(data_honest[:,:int(n_honest)].apply(np.max)))
    else:
        sns.boxplot(data=pd.melt(data_performance, id_vars=['behavior','plot_order']),
                        x='plot_order',y='value', hue='behavior',
                        linewidth=1, dodge=False,width=.5,palette="deep")
        performance_max=max(data_performance.iloc[:,:24].apply(np.max))

    fig.set_size_inches(BASE_BOX_WIDTH*n_subplots,BASE_BOX_HEIGHT+1)
    axs.set_ylim(0,25)#int(1.25*performance_max))
    #TODO AX2 YTICKS look like  "-" signs\
    if "items" in performance_index:
        performance_label="items collected"
    axs.set_ylabel(performance_label)

    if not quality_index=="":
        data_quality=pd.concat(quality_list)

        if "trans" in quality_index:
            quality_label=f"{numerator_quality}/{denominator_quality} transactions"
        elif "reward" in quality_index:
            quality_label="reward\n(each value >0)"
        quality_label=f"{quality_function} {quality_label}"
        ax2=axs.twinx()
        sns.pointplot(data=pd.melt(data_quality,id_vars=['behavior','plot_order']),palette="dark",
                        x='plot_order',y='value', hue='behavior',ax=ax2,markers="*",join=False,)

        ax2.set_ylabel(quality_label)
        axs.legend().set_visible(False)
        ax2.legend(title="quality index (right axis)"+("\n(small boxplots: dishonests)" \
            if show_dishonests else ""), loc="upper left")

        if not title:title=base_title+" with Quality Index"
    else:
        axs.legend(title="(small boxplots: dishonests)", loc="lower left", labels=[])
        if not title:title=base_title
        ax2=None

    fig.suptitle(title,fontweight="bold")
    axs.set_xticklabels(x_labels)
    axs.set_xlabel('')
    sns.despine(fig,trim=False, )

    if not multi_plot and not save_plot:plt.show()
    if save_plot:plt.savefig(f"{join(save_folder,save_name)}.png", bbox_inches='tight')


#####################################################################################
# -----------------------EXPERIMENTS PLOTTING FUNCTIONS---------------------------------- #
def compare_behaviors_performance_quality(
                                        data_folder,
                                        experiment="",
                                        experiment_part="whole",
                                        performance_metric="",
                                        quality_index="",
                                        show_dishonests=False,
                                        auto_xlabels=True,
                                        n_robots=25,
                                        n_honests=[25,24,22,],
                                        behaviours=[],
                                        behavior_params_experiments=dict(),
                                        payment_systems=["P","NP"],
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
        or a specific part of it. Refer to load_data_from_csv for more info.

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
    TODO convert names into initials

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

    if performance_metric=="items":
        if experiment_part=="whole":
            performance_folder="items_collected"
    if "last" in experiment_part:
        performance_folder=performance_metric+"_evolution"

    for n_honest in n_honests:
        lie_angle=0 if n_honest==n_robots else 90
        for noise_type in noise_type_list:
            for saboteur_performance in saboteur_performance_list:
                for noise_mu in noise_mu_list:
                    for noise_range in noise_range_list:
                        noise_params_values=[noise_mu,noise_range,saboteur_performance]
                        
                        if compare_best_of: best_list=[]
                        for payment_system in payment_systems:
                            for behavior_initials in behaviours:
                                if save_plot:
                                    behav_save_folder=join(save_folder,experiment,performance_metric,SUB_FOLDERS_DICT[behavior_initials])
                                    if not os.path.exists(behav_save_folder):os.makedirs(behav_save_folder,exist_ok=True)
                                filenames=[
                                    filename_from_params(n_honest,"n",
                                                        "NP",lie_angle,
                                                        [],
                                                        noise_type,noise_params_values),
                                    filename_from_params(n_honest,"n",
                                                        "P",lie_angle,
                                                        [],
                                                        noise_type,noise_params_values),
                                    filename_from_params(n_honest,"s",
                                                        "NP",lie_angle,
                                                        [0.25],
                                                        noise_type,noise_params_values),
                                    filename_from_params(n_honest,"s",
                                                        "P",lie_angle,
                                                        [0.25],
                                                        noise_type,noise_params_values),
                                    ]
                                filenames=[join(data_folder,experiment,SUB_FOLDERS_DICT[b_i],\
                                    performance_folder,f)+(".csv" if not f.endswith(".csv") else "")\
                                        for f,b_i in zip(filenames,['n','n','s','s'])]

                                if not auto_xlabels:
                                    x_labels=["Naive\nno penalisation","Naive\npenalisation","Sceptical\nno penalisation","Sceptical\npenalisation"]
                                else: x_labels=[]

                                for behavior_params_values in behavior_params_experiments[behavior_initials]:
                                    f=filename_from_params(n_honest,behavior_initials,
                                                            payment_system,lie_angle,
                                                            behavior_params_values,
                                                            "uniform",noise_params_values)
                                    f=join(data_folder,experiment,SUB_FOLDERS_DICT[behavior_initials],\
                                    performance_folder,f)+(".csv" if not f.endswith(".csv") else "")

                                    if not is_bad_param_combination(f):
                                        filenames.append(f)
                                        if not auto_xlabels:
                                            behavior_params_text=""
                                            for v,p in zip(behavior_params_values,BEHAVIOR_PARAMS_DICT[behavior_initials]):
                                                behavior_params_text+=f"{v} {p},\n"
                                            x_labels.append(f"{BEHAVIORS_NAME_DICT[behavior_initials]}\n"
                                            f"{behavior_params_text}"
                                            f"{'no ' if payment_system=='NP' else ''}penalis.")

                                        if compare_best_of and is_best_param_combination(f):best_list.append(f)

                                title=f"Performance comparison for {BEHAVIORS_NAME_DICT[behavior_initials]} behavior,\n"\
                                    f"{'with quality index ,' if quality_index else ''} for the {'stable part of the ' if 'last' in experiment_part else 'whole '}experiment\n"\
                                    f"for {n_honest} honests, {lie_angle}° lie angle,\n"\
                                    f"{noise_mu} mean noise, {noise_range} noise range, {'perfect' if saboteur_performance=='perf' else 'average'} saboteur performance\n"\

                                save_name=f"{n_honest}_{behavior_initials}_{payment_system}_{lie_angle}_{noise_mu}_{noise_range}_{saboteur_performance}"
                                
                                if len(filenames)==4:continue
                                performance_with_quality(
                                                        filenames,
                                                        experiment_part=experiment_part,
                                                        performance_index=performance_metric,
                                                        quality_index=quality_index,
                                                        title=title,
                                                        x_labels=x_labels,
                                                        show_dishonests=show_dishonests if n_honest<n_robots else False,
                                                        multi_plot=multi_plot,
                                                        save_plot=save_plot,
                                                        save_folder=behav_save_folder if save_plot else "",
                                                        save_name=save_name,
                                                        )
                                if multi_plot:fig_count+=1

                        if compare_best_of:
                            best_save_name=f"best_{n_honest}_{lie_angle}_{noise_mu}_{noise_range}_{saboteur_performance}"

                            best_list=filenames[:4]+[fb for b_i in behaviours for fb in best_list \
                                if params_from_filename(fb,compact_format=True)[1]==b_i]
                            performance_with_quality(
                                                    best_list,
                                                    experiment_part=experiment_part,
                                                    performance_index=performance_metric,
                                                    quality_index=quality_index,
                                                    title=title,
                                                    x_labels=x_labels,
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
                                        payment_systems=["P","NP"],
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
                for payment_system in payment_systems:
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
                    #TODO :
                    # if n_SAB>0:
                    # ["binormal","uniform,avg","uniform,perf"]
                    # else:
                    # ["bimodal","uniform, no SAB"]

                    filenames=[ filename_from_params(n_honest,behavior_initials,
                                            payment_system,lie_angle,
                                            behavior_params_values,
                                            "bimodal",bimodal_noise_params_values,),
                                filename_from_params(n_honest,behavior_initials,
                                            payment_system,lie_angle,
                                            behavior_params_values,
                                            "uniform",uniform_avg_noise_params_values),
                                filename_from_params(n_honest,behavior_initials,
                                            payment_system,lie_angle,
                                            behavior_params_values,
                                            "uniform",uniform_perf_noise_params_values)
                            ]
                    #TODO: test filenames, else remove from list filenames
                    filenames=[data_folder+experiment+"/"+SUB_FOLDERS_DICT[behavior_initials]+"/"+metric+"/"+filename+".csv" for filename in filenames]

                    save_name=filename_from_params(n_honest,behavior_initials,
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


##############################################################################################################
##############################################################################################################
if __name__ == '__main__':
    pass
    #TODO: create this as a summary from config generation / running

    # bimodal_uniform_noise_comparison(data_folder=CONFIG_FILE.DATA_FOLDER,
    #                                 experiment="",
    #                                 metric="rewards",
    #                                 n_robots=25,
    #                                 n_honests=[25,24],
    #                                 behaviors=["n","s","r","Nv","t","w"],
    #                                 behavior_params_experiments=BEHAV_PARAMS_COMBINATIONS,
    #                                 multi_plot=True,
    #                                 save_plot=False,
    #                                 save_folder=""#CONFIG_FILE.PLOT_FOLDER
    #                                 )

    # find_best_worst_seeds(filenames=[],
    #                     data_folder="../data/sceptical/",
    #                     metric="items_collected",
    #                     base_seed=5684436,
    #                     amount_to_find=3,
    #                 )

    # load_data_from_csv(filename="24r_NP_90LIA_0.3RT_0.051NMU_0.1NRANG_perfSAB.csv",
    #                 data_folder_and_subfolder=CONFIG_FILE.DATA_FOLDER+"TRANSACTION/ranking",
    #                 metric="transaction",
    #                 experiment_part="last0.66",
    #                 post_processing="col-mean"
    #                 )

compare_behaviors_performance_quality(
                                        data_folder=CONFIG_FILE.DATA_FOLDER,
                                        experiment="TRANSACTION",
                                        experiment_part="last0.66",
                                        performance_metric="items",
                                        quality_index="reward",
                                        show_dishonests=True,
                                        auto_xlabels=True,
                                        n_honests=[24,25],
                                        behaviours=['r','Nv','t','w'],
                                        behavior_params_experiments=BEHAV_PARAMS_COMBINATIONS,
                                        payment_systems=["NP","P"],
                                        saboteur_performance_list=["perf","avg"],
                                        compare_best_of=True,
                                        multi_plot=False,
                                        save_plot=True,
                                        save_folder=join(CONFIG_FILE.PLOT_FOLDER,"behav_compar_quality")
                                    )