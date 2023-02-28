import re
import os
from time import perf_counter
import argparse

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats

#percentage on axis for matplotlib
import matplotlib.ticker as mtick

from model.market import exponential_model, logistics_model
from model.navigation import Location

palette = {
    "naive": "tab:blue",
    "careful": "tab:blue",
    "smart": "tab:blue",
    "sceptical": "tab:blue",
    "greedy": "limegreen",
    "saboteur": "firebrick",
    "smartboteur": "firebrick",
    "scaboteur": "firebrick",
}


name_conversion = {
    "honest": "naive",
    "smart": "sceptical",
    "smartboteur": "scaboteur",
    "scaboteur": "scaboteur",
    "sceptical": "sceptical"
}

DATA_DIR="../data/"

comparisons=["scaboteur_rotation"
]

metrics=[
    "rewards",
    "items_collected"
]

filenames = [
            "25sceptical_3000th_0scaboteur_0rotation_nopenalisation.txt",
            "24sceptical_3000th_1scaboteur_0rotation_nopenalisation.txt",
            # "22sceptical_3000th_3scaboteur_0rotation_nopenalisation.txt",#SAME AS 24 ABOVE
            "25sceptical_3000th_0scaboteur_0rotation_penalisation.txt",
            "24sceptical_3000th_1scaboteur_0rotation_penalisation.txt",
            # "22sceptical_3000th_3scaboteur_0rotation_penalisation.txt",#same as 24 above
            "25sceptical_025th_0scaboteur_0rotation_nopenalisation.txt",
            "24sceptical_025th_1scaboteur_0rotation_nopenalisation.txt",
            "25sceptical_025th_0scaboteur_0rotation_penalisation.txt",
            "24sceptical_025th_1scaboteur_0rotation_penalisation.txt",
            # "22sceptical_025th_3scaboteur_0rotation_nopenalisation.txt",#SAME AS 24 ABOVE
            # "22sceptical_025th_3scaboteur_0rotation_penalisation.txt"
]

#------------------------------------------------------------------------------------------------
#---------------------------------------UTILITIES------------------------------------------------Ù

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


def get_file_config(filename:str):
    name_honest = re.search('[a-z]+', filename.split("_")[0]).group()
    name_saboteur = re.search('[a-z]+', filename.split("_")[2]).group()
    n_honest = int(re.search('[0-9]+', filename.split("_")[0]).group())
    n_saboteur = int(re.search('[0-9]+', filename.split("_")[2]).group())
    skepticism=re.search('[0-9]+', filename.split("_")[1]).group()
    if int(skepticism)>1340:
        if int(skepticism)>2000:
            skepticism="naive"
        else:
            skepticism="threshold naive"
    else:
        if skepticism[0]=="0":
            skepticism="0."+skepticism[1:]
        skepticism="th "+skepticism
    lie_angle=filename.split("_")[3]
    lie_angle=re.search('[0-9]+', lie_angle).group()+" "+\
        re.search('[a-z]+', lie_angle).group() \
        if n_saboteur>0 else "no saboteurs"
    penalisation=re.search('[a-z,0-9]+', filename.split("_")[4]).group()
    penalisation= "no pen" if penalisation=="nopenalisation" else "pen"
    return name_honest, n_honest,name_saboteur,n_saboteur,\
                skepticism, lie_angle,penalisation


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
                    otherwise characteristics to retrieve;
                    format string with any number of characteristics,
                    separated by "_".
                    characteristics (each one is a string):
                    - number of honests ("Nsceptical")
                    - number of saboteurs ("Mscaboteur")
                    - skepticism threshold ("Kth")
                    - lie angle ("Qrotation")
                    - penalisation ("{no,""}penalisation")
                    NOTE: ONLY FIRST TWO FILES ARE COMPARED
    '''
    PASS_THRESHOLD=0.05
    #BUG CORRECT CHOICE ORDER automatic retrieval of experiments with any robot combination,
    #  given other characteristics
    # filestocheck=[]
    # if type(filenames)==str:
    #     characteristics=filenames.split("_")
    #     filenames=[]
    #     filestocheck=os.listdir(f"{data_folder}{compare}/{metric}/")
    #     for f in filestocheck:
    #         if len(filenames)<2:
    #             for c in characteristics:
    #                 if re.search(c,f): filenames.append(f)
    #         else: break
    #     if len(filenames)<2:
    #         print("ERROR: not enough files found to compare")
    #         return
    # elif filenames==[] or len(filenames)>2:
    #     print("ERROR: please provide two filenames to \
    #         compare or characteristic to autoselect")
    #     return
    filenames = [
            # "25sceptical_3000th_0scaboteur_0rotation_nopenalisation.txt",
            # "24sceptical_3000th_1scaboteur_0rotation_nopenalisation.txt",
            # "25sceptical_3000th_0scaboteur_0rotation_penalisation.txt",
            # "24sceptical_3000th_1scaboteur_0rotation_penalisation.txt",
            # "25sceptical_025th_0scaboteur_0rotation_nopenalisation.txt",
            # "24sceptical_025th_1scaboteur_0rotation_nopenalisation.txt",
            # "25sceptical_025th_0scaboteur_0rotation_penalisation.txt",
            # "24sceptical_025th_1scaboteur_0rotation_penalisation.txt",
            #####
            # "24sceptical_3000th_1scaboteur_0rotation_nopenalisation.txt",
            # "24sceptical_025th_1scaboteur_0rotation_nopenalisation.txt"
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
                # metric="rewards",
                metric="items_collected",
                ):
    filenames = [
            # "25sceptical_3000th_0scaboteur_0rotation_nopenalisation.txt",
            # "24sceptical_3000th_1scaboteur_0rotation_nopenalisation.txt",
            # "25sceptical_3000th_0scaboteur_0rotation_penalisation.txt",
            # "24sceptical_3000th_1scaboteur_0rotation_penalisation.txt",
            # "25sceptical_025th_0scaboteur_0rotation_nopenalisation.txt",
            # "24sceptical_025th_1scaboteur_0rotation_nopenalisation.txt",
            # "25sceptical_025th_0scaboteur_0rotation_penalisation.txt",
            # "24sceptical_025th_1scaboteur_0rotation_penalisation.txt",
            ]
    data1=pd.read_csv(f"{data_folder}{compare}/{metric}/{filenames[0]}").apply(np.sum, axis=1)
    data2=pd.read_csv(f"{data_folder}{compare}/{metric}/{filenames[1]}").apply(np.sum, axis=1)
    anova_test=stats.f_oneway(data1, data2)
    print(f"F-statistic: {anova_test.statistic},\np-value: {anova_test.pvalue}\n")


#------------------------------------------------------------------------------------------------
#---------------------------------------PLOTTING-------------------------------------------------
def myboxplots(
                filenames=[],
                # comparison_method="s",
                data_folder="../data/all",\
                title="",\
                compare="",\
                # metric="rewards",
                metric="items_collected",
                mode="r",
                by=1
                ):
    '''
    :param filenames: list of filenames to compare,
                    if empty all the files in the folder are fetched
    TODO: if filenames is a list of lists, each sublist is a group of files to compare with different hue
            should introduce a param to understand if must compare withing a group or between groups
    :param comparison_method: "s" for single, "w" for within, "b" for between

    :param mode: "s" for standalone, "c" for cumulative, "r" for relative
    '''
    BASE_BOX_WIDTH=3
    BASE_BOX_HEIGHT=7
    filenames = [
                "24sceptical_3000th_1scaboteur_0rotation_nopenalisation.txt"
    ]
    if filenames==[]:
        filenames=os.listdir(f"{data_folder}{compare}/{metric}/")
        #TODO is the following better?
        # filenames=[f for f in os.listdir(use_dir) if os.path.isfile(os.path.join(use_dir, f))]
    n_boxes=len(filenames)// by
    fig, axs = plt.subplots(by, n_boxes, sharey=True)
    fig.set_size_inches(BASE_BOX_WIDTH*n_boxes,BASE_BOX_HEIGHT)
    # fig.supxlabel()
    sns.set_style("whitegrid")
    for idx,filename in enumerate(filenames):
        name_honest, n_honest,name_saboteur,n_saboteur,\
            skepticism, lie_angle,penalisation=get_file_config(filename)
        # params=f"{n_honest} honests,\n{skepticism},\n {lie_angle},\n {penalisation}"
        # axs[idx].set_xlabel(params)
        filename=f"{data_folder}{compare}/{metric}/{filename}"
        match mode:
            case "r":#RELATIVE DATA
                #TODO correct?
                data=pd.read_csv(filename, header=None).to_numpy()
                print(type(data))
                data=(100*data/np.sum(data,axis=1)[:,None]).flatten()
                #TODO could use title functions inside plot calls
                sns.boxplot(data=data,ax=axs[idx]).set(xticklabels=[],xticks=[])
                data_title=metric+ " (relative)"
                axs[idx].yaxis.set_major_formatter(mtick.PercentFormatter())
            case "c":#CUMULATIVE DATA
                data=pd.read_csv(filename, header=None)
                datatot = data.apply(np.sum, axis=1)
                sns.boxplot(data=datatot,ax=axs[idx]).set(xticklabels=[],xticks=[])
                # angle = 10 * (idx + 0)
                # sns.boxplot(x=[angle for _ in batch_total], y=data, ax=axs[idx], linewidth=2)
                data_title=metric+ " (cumulative)"
            case "s":#STANDALONE DATA
                data=pd.read_csv(filename, header=None).values.flatten()
                sns.boxplot(data=data.flatten(),ax=axs[idx]).set(xticklabels=[],xticks=[])
                data_title=metric+ " (standalone)"
    sns.despine(fig, axs[idx], trim=False)
    fig.supylabel(data_title.replace("_"," "))
    title=title if title!="" else f"compare: {compare}".replace("_"," ")
    # title=title if title!="" else f"compare: {compare}\n{n_honest} {name_honest} vs {n_saboteur} {name_saboteur}".replace("_"," ")
    fig.suptitle(title,fontweight="bold")
    plt.ylim(bottom=0)
    plt.show()


def boxplots_pen_lie(
                filenames=[],
                data_folder="../data/penalisation_investigation/",\
                metric="items_collected",
                by=1
                ):
    '''
    this function uses as input not headed, numeric rows, csv files, containing the final values for each run
    for the data analysis at others steps use the function below
    TODO: unify with the one below
    '''
    BASE_BOX_WIDTH=3
    BASE_BOX_HEIGHT=7
    filenames=[
                [
                ],[
                ]
            ]
    labels=["no penalisation","penalisation"]
    columns_labels=["items collected", "lie angle"]
    SUPTITLE="COMPARING PENALISATION (WITH AND WITHOUT)\nAT DIFFERENT LIE ANGLES\n"\
            "FOR 22 SCEPTICALS AND 3 SCABOTEUR\nFOR STABLE PART OF THE EXPERIMENT"
    n_boxes=len(filenames[0])// by
    fig, axs = plt.subplots(by, n_boxes, sharey=True)
    fig.set_size_inches(BASE_BOX_WIDTH*n_boxes,BASE_BOX_HEIGHT+1)
    for idx,(f_nopen,f_pen) in enumerate(zip(filenames[0],filenames[1])):
        list_nopen=pd.read_csv(f"{data_folder}{metric}/{f_nopen}", header=None).apply(np.sum, axis=1)#Series
        list_pen=pd.read_csv(f"{data_folder}{metric}/{f_pen}", header=None).apply(np.sum, axis=1)
        list_nopen_flat = pd.DataFrame(list_nopen.to_numpy().flatten()) #Dataframe(ndarray)
        list_pen_flat = pd.DataFrame(list_pen.to_numpy().flatten())
        ttest_pv=stats.ttest_ind(list_nopen_flat,list_pen_flat)[1][0]
        list_nopen= pd.DataFrame(np.full(list_nopen_flat.shape, labels[0]))
        list_pen= pd.DataFrame(np.full(list_pen_flat.shape, labels[1]))
        list_nopen_flat = pd.concat([list_nopen_flat, list_nopen], axis=1)
        list_pen_flat = pd.concat([list_pen_flat, list_pen], axis=1)
        data = pd.concat([list_nopen_flat, list_pen_flat])
        data.columns = columns_labels
        if idx==0:
            sns.boxplot(data=data,y=data.columns[0],x=columns_labels[1],hue=columns_labels[1],linewidth=1, dodge=False, ax=axs[idx]).set(
                 xlabel=None,ylabel=None,xticklabels=[],xticks=[])
            axs[idx].set_ylabel("totat items collected")
        else:
            sns.boxplot(data=data,y=data.columns[0],x=columns_labels[1],linewidth=1, dodge=False, ax=axs[idx]).set(
                xlabel=None, ylabel=None,xticklabels=[],xticks=[])
        lie_angle=idx*10
        ttest_th=0.05
        params=f"{lie_angle},\nT-test (thr={ttest_th})\np-value: \n{np.round(ttest_pv,5)}"
        axs[idx].set_xlabel(params)
    plt.ylim(bottom=0)
    sns.despine(fig, axs[idx], trim=False)
    fig.suptitle(SUPTITLE,fontweight="bold")
    plt.show()


def boxplot_evo_pen_lie(
                filenames=[],
                data_folder="../data/reputation/",\
                metric="items_evolution",
                by=1
                ):
    '''
    this function uses as input not headed, numeric rows, csv files
    '''
    BASE_BOX_WIDTH=3
    BASE_BOX_HEIGHT=7
    filenames=[
                # [
                # "24c_np_03tr_0r.csv",
                # "24c_np_03tr_90r.csv"
                # ],[
                # "24c_p_03tr_0r.csv",
                # "24c_p_03tr_90r.csv"
                # ]
                [
                "22c_np_03tr_0r.csv",
                "22c_np_03tr_90r.csv"
                ],[
                "22c_p_03tr_0r.csv",
                "22c_p_03tr_90r.csv"
                ]
            ]
    labels=["no penalisation","penalisation"]
    columns_labels=["items collected", "lie angle"]
    n_boxes=len(filenames[0])// by
    fig, axs = plt.subplots(by, n_boxes, sharey=True)
    for idx,(f_nopen,f_pen) in enumerate(zip(filenames[0],filenames[1])):
        filename_nopen=f"{data_folder}{metric}/{f_nopen}"
        filename_pen=f"{data_folder}{metric}/{f_pen}"
        #TODO OPTIMIZE THIS IS SO SLOW
        nopen_df = pd.read_csv(filename_nopen,converters={'items_list': pd.eval})
        per_df = pd.read_csv(filename_pen,converters={'items_list': pd.eval})
        labels=nopen_df.columns.to_list()
        selected_runs=nopen_df[labels[0]].unique()
        nopen_data=[]; pen_data=[]
        for run in selected_runs:
            nopen_run_row=nopen_df.loc[lambda df: df[labels[0]] == run].iloc[:,-1]
            pen_run_row=per_df.loc[lambda df: df[labels[0]] == run].iloc[:,-1]
            nopen_last=nopen_run_row.iloc[-1]
            pen_last=pen_run_row.iloc[-1]
            # nopen_end_transitory=nopen_run_row.iloc[2*len(nopen_run_row)//3]
            # pen_end_transitory=pen_run_row.iloc[2*len(pen_run_row)//3]
            # delta_nopen=nopen_last-nopen_end_transitory
            # delta_pen=pen_last-pen_end_transitory
            # nopen_data.append([delta_nopen.sum()])
            # pen_data.append([delta_pen.sum()])
            nopen_data.append([nopen_last.sum()])
            pen_data.append([pen_last.sum()])
        list_nopen_flat = pd.DataFrame(nopen_data)
        list_pen_flat = pd.DataFrame(pen_data)
        ttest_pv=stats.ttest_ind(list_nopen_flat,list_pen_flat)[1][0]
        list_nopen= pd.DataFrame(np.full(list_nopen_flat.shape, labels[0]))
        list_pen= pd.DataFrame(np.full(list_pen_flat.shape, labels[1]))
        list_nopen_flat = pd.concat([list_nopen_flat, list_nopen], axis=1)
        list_pen_flat = pd.concat([list_pen_flat, list_pen], axis=1)
        data = pd.concat([list_nopen_flat, list_pen_flat])
        data.columns = columns_labels
        #TODO FIX LEGEND
        if idx==0:
            sns.boxplot(data=data,y=data.columns[0],x=columns_labels[1],hue=columns_labels[1],linewidth=1, dodge=False, ax=axs[idx]).set(
                 xlabel=None,ylabel=None,xticklabels=[],xticks=[])
            axs[idx].set_ylabel("totat items collected")
        else:
            sns.boxplot(data=data,y=data.columns[0],x=columns_labels[1],linewidth=1, dodge=False, ax=axs[idx]).set(
                xlabel=None, ylabel=None,xticklabels=[],xticks=[])
        lie_angle=idx*10
        ttest_th=0.05
        params=f"{lie_angle},\nT-test (thr={ttest_th})\np-value: \n{np.round(ttest_pv,5)}"
        axs[idx].set_xlabel(params)
    fig.set_size_inches(BASE_BOX_WIDTH*n_boxes,BASE_BOX_HEIGHT+1)
    fig.suptitle("COMPARING PENALISATION (WITH AND WITHOUT)\nAT DIFFERENT LIE ANGLES\n"\
    "FOR 24 SCEPTICALS AND 1 SCABOTEUR\nFOR LAST 5000 STEPS OF THE EXPERIMENT, SEEDED",fontweight="bold")
    plt.ylim(bottom=0)
    sns.despine(fig, axs[idx], trim=False)
    plt.show()


def boxplot_repu(
                filenames=[],
                data_folder="../data/reputation/",\
                metric="items_evolution",
                by=1
                ):
    '''
    this function uses as input not headed, numeric rows, csv files
    '''
    BASE_BOX_WIDTH=3
    BASE_BOX_HEIGHT=7
    filenames=[
                [
                "22n_p_0r.csv",
                "22n_p_90r.csv",
                ],
                # [
                # "22c_np_03tr_0r.csv",
                # "22c_np_03tr_90r.csv",
                # ],
                [
                "22c_p_05tr_0r.csv",
                "22c_p_05tr_90r.csv",
                ],
                # [
                # "22c_np_08tr_0r.csv",
                # "22c_np_08tr_90r.csv",
                # ],
                [
                "22c_p_11tr_0r.csv",
                "22c_p_11tr_90r.csv",
                ]
            ]
    """
    plot:   n,c03, c05, c08
            lie ancgle 0..............lie angle 90

    22c_np_03tr_0r.csv
    22c_np_03tr_90r.csv
    22c_np_05tr_0r.csv
    22c_np_05tr_90r.csv
    22c_np_08tr_0r.csv
    22c_np_08tr_90r.csv
    22c_p_03tr_0r.csv
    22c_p_03tr_90r.csv
    22c_p_05tr_0r.csv
    22c_p_05tr_90r.csv
    22c_p_08tr_0r.csv
    22c_p_08tr_90r.csv
    22n_p_0r.csv
    22n_p_90r.csv

    24c_np_03tr_0r.csv
    24c_np_03tr_90r.csv
    24c_np_05tr_0r.csv
    24c_np_05tr_90r.csv
    24c_np_08tr_0r.csv
    24c_np_08tr_90r.csv
    24c_p_03tr_0r.csv
    24c_p_03tr_90r.csv
    24c_p_05tr_0r.csv
    24c_p_05tr_90r.csv
    24c_p_08tr_0r.csv
    24c_p_08tr_90r.csv
    24n_p_0r.csv
    24n_p_90r.csv
    """
    experiments_labels=["naive (penalized)","choosy 0.5 (threshold)","choosy 1.1"]
    # experiments_labels=["naive","choosy 0.3 (treshold)","choosy 0.5","choosy 0.8","choosy 1.1"]
    new_labels=["items collected", "agent type"]
    n_boxes=len(filenames[0])// by
    fig, axs = plt.subplots(by, n_boxes, sharey=True)
    # for idx,(f_naive,f_03tr,f_05tr,f_08tr,f_11tr,) in enumerate(zip(filenames[0],
    for idx,(f_naive,f_05tr,f_11tr,) in enumerate(zip(filenames[0],
                                                                    filenames[1],
                                                                    filenames[2],
                                                                    # filenames[3],
                                                                    # filenames[4]
                                                                    )):
        filename_naive=f"{data_folder}{metric}/{f_naive}"
        # filename_f_03tr=f"{data_folder}{metric}/{f_03tr}"
        filename_f_05tr=f"{data_folder}{metric}/{f_05tr}"
        # filename_f_08tr=f"{data_folder}{metric}/{f_08tr}"
        filename_f_11tr=f"{data_folder}{metric}/{f_11tr}"
        #TODO OPTIMIZE THIS IS SO SLOW
        naive_df = pd.read_csv(filename_naive,converters={'items_list': pd.eval})
        # f_03tr_df = pd.read_csv(filename_f_03tr,converters={'items_list': pd.eval})
        f_05tr_df = pd.read_csv(filename_f_05tr,converters={'items_list': pd.eval})
        # f_08tr_df = pd.read_csv(filename_f_08tr,converters={'items_list': pd.eval})
        f_11tr_df = pd.read_csv(filename_f_11tr,converters={'items_list': pd.eval})
        labels=naive_df.columns.to_list()
        selected_runs=naive_df[labels[0]].unique()
        naive_data=[]
        # f_03tr_data=[]
        f_05tr_data=[]
        # f_08tr_data=[]
        f_11tr_data=[]
        for run in selected_runs:
            naive_run_row=naive_df.loc[lambda df: df[labels[0]] == run].iloc[:,-1]
            # f_03tr_run_row=f_03tr_df.loc[lambda df: df[labels[0]] == run].iloc[:,-1]
            f_05tr_run_row=f_05tr_df.loc[lambda df: df[labels[0]] == run].iloc[:,-1]
            # f_08tr_run_row=f_08tr_df.loc[lambda df: df[labels[0]] == run].iloc[:,-1]
            f_11tr_run_row=f_11tr_df.loc[lambda df: df[labels[0]] == run].iloc[:,-1]
            naive_last=naive_run_row.iloc[-1]
            # f_03tr_last=f_03tr_run_row.iloc[-1]
            f_05tr_last=f_05tr_run_row.iloc[-1]
            # f_08tr_last=f_08tr_run_row.iloc[-1]
            f_11tr_last=f_11tr_run_row.iloc[-1]
            # nopen_end_transitory=nopen_run_row.iloc[2*len(nopen_run_row)//3]
            # pen_end_transitory=pen_run_row.iloc[2*len(pen_run_row)//3]
            # delta_nopen=nopen_last-nopen_end_transitory
            # delta_pen=pen_last-pen_end_transitory
            # nopen_data.append([delta_nopen.sum()])
            # pen_data.append([delta_pen.sum()])
            naive_data.append([naive_last.sum()])
            # f_03tr_data.append([f_03tr_last.sum()])
            f_05tr_data.append([f_05tr_last.sum()])
            # f_08tr_data.append([f_08tr_last.sum()])
            f_11tr_data.append([f_11tr_last.sum()])
        list_naive_flat = pd.DataFrame(naive_data)
        # list_f_03tr_flat = pd.DataFrame(f_03tr_data)
        list_f_05tr_flat = pd.DataFrame(f_05tr_data)
        # list_f_08tr_flat = pd.DataFrame(f_08tr_data)
        list_f_11tr_flat = pd.DataFrame(f_11tr_data)
        # ttest_pv=stats.ttest_ind(list_nopen_flat,list_pen_flat)[1][0]
        list_naive= pd.DataFrame(np.full(list_naive_flat.shape, experiments_labels[0]))
        # list_f_03tr= pd.DataFrame(np.full(list_f_03tr_flat.shape, experiments_labels[1]))
        # list_f_05tr= pd.DataFrame(np.full(list_f_05tr_flat.shape, experiments_labels[2]))
        list_f_05tr= pd.DataFrame(np.full(list_f_05tr_flat.shape, experiments_labels[1]))
        # list_f_08tr= pd.DataFrame(np.full(list_f_08tr_flat.shape, experiments_labels[3]))
        # list_f_11tr= pd.DataFrame(np.full(list_f_11tr_flat.shape, experiments_labels[4]))
        list_f_11tr= pd.DataFrame(np.full(list_f_11tr_flat.shape, experiments_labels[2]))
        list_naive_flat = pd.concat([list_naive_flat, list_naive], axis=1)
        # list_f_03tr_flat = pd.concat([list_f_03tr_flat, list_f_03tr], axis=1)
        list_f_05tr_flat = pd.concat([list_f_05tr_flat, list_f_05tr], axis=1)
        # list_f_08tr_flat = pd.concat([list_f_08tr_flat, list_f_08tr], axis=1)
        list_f_11tr_flat = pd.concat([list_f_11tr_flat, list_f_11tr], axis=1)
        data = pd.concat([  list_naive_flat,
                            # list_f_03tr_flat,
                            list_f_05tr_flat,
                            # list_f_08tr_flat,
                            list_f_11tr_flat
                        ])
        data.columns = new_labels
        if idx==0:
            sns.boxplot(data=data,y=data.columns[0],x=new_labels[1],hue=new_labels[1],linewidth=1, dodge=False, ax=axs[idx]).set(
                 xlabel=None,ylabel=None,xticklabels=[],xticks=[])
            axs[idx].set_ylabel("totat items collected")
        else:
            sns.boxplot(data=data,y=data.columns[0],x=new_labels[1],linewidth=1, dodge=False, ax=axs[idx]).set(
                xlabel=None, ylabel=None,xticklabels=[],xticks=[])
        lie_angle=idx*90
        # ttest_th=0.05
        params=f"{lie_angle}"#,\nT-test (thr={ttest_th})\np-value: \n{np.round(ttest_pv,5)}"
        axs[idx].set_xlabel(params)
    fig.set_size_inches(BASE_BOX_WIDTH*n_boxes,BASE_BOX_HEIGHT+1)
    fig.suptitle("COMPARING REPUTATION THRESHOLD (WITH PEN)\nAT DIFFERENT LIE ANGLES\n"\
    "FOR 22 CHOOSY AND 1 CHOOSOTEUR\nALL OF THE EXPERIMENT, SEEDED",fontweight="bold")
    plt.ylim(bottom=0)
    sns.despine(fig, axs[idx], trim=False)
    plt.show()


# def boxplot_evo_test(
#                 data_folder="../data/reputation/",\
#                 metric="items_evolution",
#                 ):
#     BASE_BOX_WIDTH=3
#     BASE_BOX_HEIGHT=7
#     filenames=[
#                 [
#                 "22n_p_0r.csv",
#                 "22n_p_90r.csv",
#                 ],
#                 [
#                 "22c_np_03tr_0r.csv",
#                 "22c_np_03tr_90r.csv",
#                 ],
#                 [
#                 "22c_np_05tr_0r.csv",
#                 "22c_np_05tr_90r.csv",
#                 ],
#                 [
#                 "22c_np_08tr_0r.csv",
#                 "22c_np_08tr_90r.csv",
#                 ]
#             ]
#     labels=["naive","reputation 0.3","reputation 0.5","reputation 0.8",]
#     columns_labels=["items collected", "lie angle"]
#     n_boxes=len(filenames[0])
#     fig, axs = plt.subplots(1, n_boxes, sharey=True)
#     for idx in range(len(filenames[0])):#for all lie angles
#         data=pd.DataFrame([])
#         for f in filenames:#for all idx-th elements of nested level
#             filename=f"{data_folder}{metric}/{f[idx]}"
#             df = pd.read_csv(filename,converters={'items_list': pd.eval})
#             labels=df.columns.to_list()
#             selected_runs=df[labels[0]].unique()
#             file_data=[]
#             for run in selected_runs:
#                 file_run_row=df.loc[lambda df: df[labels[0]] == run].iloc[:,-1]
#                 file_last_row=file_run_row.iloc[-1]
#                 file_data.append([file_last_row.sum()])
#             list_file_flat = pd.DataFrame(file_data)
#             # ttest_pv=stats.ttest_ind(list_file_flat,list_pen_flat)[1][0]
#             list_file= pd.DataFrame(np.full(list_file_flat.shape, labels[0]))
#             list_file_flat = pd.concat([list_file_flat, list_file], axis=1)
#             data = pd.concat([data,list_file_flat])
#         data.columns = columns_labels
#         if idx==0:
#             sns.boxplot(data=data,y=data.columns[0],x=columns_labels[1],hue=columns_labels[1],linewidth=1, dodge=False, ax=axs[idx]).set(
#                  xlabel=None,ylabel=None,xticklabels=[],xticks=[])
#             axs[idx].set_ylabel("totat items collected")
#         else:
#             sns.boxplot(data=data,y=data.columns[0],x=columns_labels[1],linewidth=1, dodge=False, ax=axs[idx]).set(
#                 xlabel=None, ylabel=None,xticklabels=[],xticks=[])
#         lie_angle=idx*10
#         ttest_th=0.05
#         params=f"{lie_angle}"#,\nT-test (thr={ttest_th})\np-value: \n{np.round(ttest_pv,5)}"
#         axs[idx].set_xlabel(params)
#     fig.set_size_inches(BASE_BOX_WIDTH*n_boxes,BASE_BOX_HEIGHT+1)
#     fig.suptitle("COMPARING PENALISATION (WITH AND WITHOUT)\nAT DIFFERENT LIE ANGLES\n"\
#     "FOR 24 SCEPTICALS AND 1 SCABOTEUR\nFOR LAST 5000 STEPS OF THE EXPERIMENT, SEEDED",fontweight="bold")
#     plt.ylim(bottom=0)
#     sns.despine(fig, axs[idx], trim=False)
#     plt.show()


def plot_evolution( filename=[],
                    data_folder="../data/new/",
                    metric="items_evolution",
                    compare=""
                    ):
    """
    plot evolution of metric during simulation steps
    params:
        filename: list of filenames to plot
        data_folder: folder where to find data
        metric: metric to plot
        title: title of plot
        compare: comparison method, could be
            - "a": plot all experiments with similar configuration.
                    In this case a single filename is expected;
            - "g": plot in aggregated form experiments with similar
                    configuration. In this case a filename and a list of
                    statistics are expected. Accepted statistics are:
                    - "m": mean of all experiments (ie: gm);
                    - "s": standard deviation of all experiments;
                    - "lM": lower bound of M% confidence interval (eg: gl95);
                    - "uM": upper bound of M% confidence interval;
                    - "e" standard error of the mean;
                    - "pM": percentile interval of M% confidence interval;
                    - "cM": confidence interval of M% confidence interval;
            - "dN": plot 2 experiments with same seed, but different
                    penalisation method. In this case 2 filenames are expected,
                    as well as N the number of the experiment to compare (e.g p1);
            - "w":  compare diffetent starting wealths
            - "n":  comapre different noise intensities
    """
    fig=plt.figure(0)
    fig.set_size_inches(6,5)
    filenames=["pen_P.csv"]
    # filenames=["pen_P.csv", "pen.csv", "pen_R.csv"]
    # palettes=["flare","Set2","cubehelix"]
    legends=['poor']
    # legends=['poor','base','rich']
    # legends=['noisier','base','denoised']
    for filename_pen, legend in zip(filenames,legends):
        pen_df=pd.read_csv(f"{data_folder}/{metric}/{filename_pen}",converters={"items_list": pd.eval})
        labels=pen_df.columns.to_list()
        # selected_runs=re.search(r"p(\d+)",compare).group(1) if this results empty
        selected_runs=pen_df[labels[0]].unique()
        run_data=[]
        for run in selected_runs:
            run_pen_data=[]
            run_pen_df=pen_df.loc[lambda df: df[labels[0]] == run].iloc[:,-1].to_numpy()
            for step in range(len(run_pen_df)):
                step_df=np.sum(run_pen_df[step])
                run_pen_data.append(step_df)
            run_data.extend(run_pen_data)
        pen_df=pd.concat([pen_df,pd.DataFrame(run_data, columns=['items_sum'])],axis=1)
        if "a" in compare:
            sns.lineplot(data=pen_df, x=labels[1], y='items_sum', hue=labels[0],\
                legend=None).set_xticks(pen_df[labels[1]].unique()[::5])
            # plt.ylim(-10,500)
            plt.legend(loc='upper left')
        elif "g" in compare:
            # sns.lineplot(data=pen_df, x=labels[1], y='items_sum', errorbar=("ci",90),estimator="median",\
            #     legend=None).set_xticks(pen_df[labels[1]].unique()[::5])#random bootstrap
            # sns.lineplot(data=pen_df, x=labels[1], y='items_sum', errorbar=("sd"),\
            #     legend=None).set_xticks(pen_df[labels[1]].unique()[::5])#default:+-1 sd
            sns.lineplot(data=pen_df, x=labels[1], y='items_sum', errorbar=("pi",50),\
                legend='auto').set_xticks(pen_df[labels[1]].unique()[::5])#interquartile range
            sns.lineplot(data=pen_df, x=labels[1], y='items_sum', errorbar=(lambda x: (x.min(),x.max())),\
                legend='auto',label=legends).set_xticks(pen_df[labels[1]].unique()[::5])#== pi 100
            plt.legend(loc='upper left',labels=["mean","pi 50","min-max"])
            plt.title(f"aggregated data ({len(selected_runs)}),\n"\
                "24 scepticals, 0.25 threshold,0 rotation,\nno penalisation, POOR")
            # plt.ylim(-10,500)
        elif "s" in compare:
            sns.lineplot(x=pen_df[labels[1]],y=pen_df['items_sum'],label=legend)
            plt.legend(loc='upper left')
    plt.xticks(rotation=45)
    plt.xlabel("steps")
    plt.ylabel("total items collected")
    plt.show()
    plt.show()


#######################################################################################
#######################################################################################

def main():
    dec_const = pd.read_csv("../data/old_data/results_decaying_constant.txt", header=None).values.flatten()
    w_dec_const = pd.read_csv("../data/old_data/results_weighteddecaying_constant.txt", header=None).values.flatten()
    better = pd.read_csv("../data/old_data/results_betterage.txt", header=None).values.flatten()
    w_better = pd.read_csv("../data/old_data/results_weightedbetterage.txt", header=None).values.flatten()
    dec_lin = pd.read_csv("../data/old_data/results_decaying_linearnoise.txt", header=None).values.flatten()
    w_dec_lin = pd.read_csv("../data/old_data/results_weighteddecaying_linearnoise.txt", header=None).values.flatten()
    dec_exp = pd.read_csv("../data/old_data/results_decaying_expnoise.txt", header=None).values.flatten()
    w_dec_exp = pd.read_csv("../data/old_data/results_weighteddecaying_expnoise.txt", header=None).values.flatten()
    dec_exp_const = pd.read_csv("../data/old_data/results_decaying_expconst.txt", header=None).values.flatten()
    # print(dec_const.mean(axis=1).mean())
    # print(better.mean(axis=1).mean())
    # print(dec_lin.mean(axis=1).mean())
    fig, axs = plt.subplots(1, 6, sharey=True)
    fig.set_size_inches(12, 6)
    pd.DataFrame(dec_const).boxplot(ax=axs[0]).set_title("Decaying Constant")
    pd.DataFrame(w_dec_const).boxplot(ax=axs[1]).set_title("W-Decaying Constant")
    # pd.DataFrame(better).boxplot(ax=axs[2]).set_title("Better Age")
    # pd.DataFrame(w_better).boxplot(ax=axs[3]).set_title("W-Better Age")
    pd.DataFrame(dec_lin).boxplot(ax=axs[2]).set_title("Decaying Linear")
    pd.DataFrame(w_dec_lin).boxplot(ax=axs[3]).set_title("W-Decaying Linear")
    pd.DataFrame(dec_exp).boxplot(ax=axs[4]).set_title("Decaying Exp")
    pd.DataFrame(w_dec_exp).boxplot(ax=axs[5]).set_title("W-Decaying Exp")
    # pd.DataFrame(dec_exp_const).boxplot(ax=axs[5]).set_title("Dec Exp Const")
    plt.show()


def main2():
    df = pd.read_csv("../data/behaviors/rewards/25honest.txt", header=None)
    plt.plot(df.apply(np.mean, axis=0))
    plt.show()


def compare_strats():
    strats = ["age", "w-age", "lin", "w-lin", "exp", "w-exp"]
    strats_translated = {
        "age": "Constant",
        "w-age": "W-Constant",
        "lin": "Linear",
        "w-lin": "W-Linear",
        "exp": "Exponential",
        "w-exp": "W-Exponential"
    }
    mu_folders = ["low_0", "med_05", "high_10"]
    sd_folders = ["low_01", "high_10"]
    popsize_folders = {"low_10", "high_50"}
    d = {"mu": mu_folders, "sd": sd_folders, "popsize": popsize_folders}
    for f1 in d:
        fig, axs = plt.subplots(1, len(d[f1]), sharey=True)
        fig.suptitle("Comparing different ways to decrease quality and to combine location information")
        fig.set_size_inches(8 * len(d[f1]), 6)
        for i, f2 in enumerate(d[f1]):
            print(axs[i])
            items_tot = []
            strategies_tot = []
            for s in strats:
                items = (pd.read_csv(f"../data/quality_comp/{f1}/{f2}/{s}.txt",
                                     header=None).values.flatten() - 3).tolist()
                strategies = [strats_translated[s] for item in items]
                strategies_tot += strategies
                items_tot += items
            df = pd.DataFrame(items_tot)
            df.columns = ["Number of Items Collected"]
            df["Strategy"] = strategies_tot

            title = ""
            match f1:
                case "mu":
                    title = f"m = 0.{f2.split('_')[1]}, s = 0.05, N = 25"
                case "sd":
                    title = f"m = 0.05, s = 0.{f2.split('_')[1]}, N = 25"
                case "popsize":
                    title = f"m = 0.05, s = 0.05, N = {f2.split('_')[1]}"

            sns.boxplot(data=df, x="Strategy", y="Number of Items Collected", linewidth=2, ax=axs[i])
            axs[i].set_title(title)
        plt.show()


def compare_behaviors():
    filenames = ["25careful", "25smart_t25",  # "25smart_t25",
                 "24careful_s3_1saboteur", "24smart_t25_1saboteur",  # "24smart_t25_1greedy",
                 "23careful_2saboteur", "23smart_t25_2saboteur",  # "23smart_t25_2greedy",
                 "22careful_3saboteur", "22smart_t25_3saboteur",  # "22smart_t25_3greedy",
                 "20careful_s3_5saboteur", "20smart_t25_5saboteur"  # , "20smart_t25_5greedy"
                 ]
    show_run_proportions(filenames, by=2)
    filenames = ["25honest", "25careful", "25smart_t25",
                 "24honest_1saboteur", "24careful_s3_1saboteur", "24smart_t25_1saboteur"]
    rewards_plot(filenames)
    show_run_proportions(filenames, by=3)
    filenames = [
        "25honest", "25smart_t10", "25smart_t25", "25smart_t40_0saboteur", "25smart_t100_0saboteur",
        "24honest_1saboteur", "24smart_t10_1saboteur", "24smart_t25_1saboteur", "24smart_t40_1saboteur",
        "24smart_t100_1saboteur"
    ]
    show_run_proportions(filenames, by=5)
    filenames = ["24smart_t25_1greedy", "24smart_t25_1greedy_minus10",
                 "22smart_t25_3greedy", "22smart_t25_3greedy_minus10",
                 "20smart_t25_5greedy", "20smart_t25_5greedy_minus10"]
    show_run_proportions(filenames, by=2)
    filenames = ["25honest", "25careful", "25smart_t25"]
    show_run_difference(filenames, by=3, metric="items_collected")
    filenames = ["24honest_1saboteur", "24careful_s3_1saboteur", "24smart_t25_1saboteur"]
    show_run_difference(filenames, by=3, metric="items_collected")


def powerpoint_plots():
    # filenames = ["24smart_t25_1greedy",
    #              "22smart_t25_3greedy",
    #              "20smart_t25_5greedy"]
    # # show_run_proportions(filenames, by=3)
    # make_violin_plots(filenames, by=3)
    # filenames = ["24smart_t25_1greedy_SoR_50",
    #              "22smart_t25_3greedy_SoR_50",
    #              "20smart_t25_5greedy_SoR_50"]
    # make_violin_plots(filenames, by=3, comparison_on="payment_types")
    # # show_run_proportions(filenames, by=3, comparison_on="payment_types")
    # filenames = ["24smart_t25_1saboteur",
    #              "22smart_t25_3saboteur",
    #              "20smart_t25_5saboteur"]
    # make_violin_plots(filenames, by=3)
    # # show_run_proportions(filenames, by=3)
    # filenames = ["24smart_t25_1saboteur_SoR_50",
    #              "22smart_t25_3saboteur_SoR_50",
    #              "20smart_t25_5saboteur_SoR_50"]
    # make_violin_plots(filenames, by=3, comparison_on="payment_types")
    # # show_run_proportions(filenames, by=3, comparison_on="payment_types")
    # filenames = ["24smart_t25_1smartboteur_SoR_50",
    #              "22smart_t25_3smartboteur_SoR_50",
    #              "20smart_t25_5smartboteur_SoR_50"]
    # make_violin_plots(filenames, by=3, comparison_on="saboteur_comp", title="Individual Share of Items Collected", metric="items_collected")
    # make_violin_plots(filenames, by=3, comparison_on="saboteur_comp", title="Individual Share of Total Reward")
    #
    # show_run_proportions(filenames, by=3, comparison_on="saboteur_comp")
    filenames = ["24smart_t25_1smartboteur_SoR_50_RTmarket",
                 "22smart_t25_3smartboteur_SoR_50_RTmarket",
                 "20smart_t25_5smartboteur_SoR_50_RTmarket"]
    make_violin_plots(filenames, by=3, comparison_on="saboteur_comp",
                      title="Share of Reward based on Round-Trip Duration")
    # # show_run_proportions(filenames, by=3, comparison_on="saboteur_comp")
    # filenames = ["24smart_t25_1smartboteur_windowdev_50_fixedmarket",
    #              "22smart_t25_3smartboteur_windowdev_50_fixedmarket",
    #              "20smart_t25_5smartboteur_windowdev_50_fixedmarket"]
    # make_violin_plots(filenames, by=3, comparison_on="saboteur_comp", title="Window Filter Reward Share Transactions, Fixed Reward")
    #
    filenames = ["24smart_t25_1smartboteur_windowdev_50_RTmarket_bis",
                 "22smart_t25_3smartboteur_windowdev_50_RTmarket_bis",
                 "20smart_t25_5smartboteur_windowdev_50_RTmarket_bis"]
    make_violin_plots(filenames, by=3, comparison_on="saboteur_comp",
                      title="Window Filter and Round-Trip Duration Reward")
    # show_run_proportions(filenames, by=3, comparison_on="saboteur_comp")
    # filenames = ["24smart_t25_1smartboteur_error^2dev_50_RTmarket",
    #              "22smart_t25_3smartboteur_error^2dev_50_RTmarket",
    #              "20smart_t25_5smartboteur_error^2dev_50_RTmarket"]
    # make_violin_plots(filenames, by=3, comparison_on="saboteur_comp", title="Square Error Filter Payment, Round Trip Market")
    # filenames = ["24smart_t25_1smartboteur_deltatime_50_RTmarket",
    #              "22smart_t25_3smartboteur_deltatime_50_RTmarket",
    #              "20smart_t25_5smartboteur_deltatime_50_RTmarket"]
    # make_violin_plots(filenames, by=3, comparison_on="saboteur_comp", title="Delta Time Payment, Round Trip Market")
    filenames = ["24smart_t25_1smartgreedy_windowdev_50_RTmarket",
                 "22smart_t25_3smartgreedy_windowdev_50_RTmarket",
                 "20smart_t25_5smartgreedy_windowdev_50_RTmarket"]
    make_violin_plots(filenames, by=3, comparison_on="saboteur_comp",
                      title="Window Filter and Round-Trip Duration Reward")
    filenames = ["25honest_t25_1smartboteur_windowdev_50_RTmarket_bis",
                 "22smart_t25_3smartboteur_windowdev_50_RTmarket_bis"]


def compare_payment_types():
    filenames = []
    for i in [25, 24, 22, 20]:
        j = 25 - i
        filenames.append(f"{i}smart_t25_{j}greedy_50_infocost_fixed")
        filenames.append(f"{i}smart_t25_{j}greedy_50_infocost_timevarying")
    show_run_proportions(filenames, by=2, comparison_on="payment_types", metric="rewards")
    show_run_proportions([filenames[i] for i in [1, 3, 5, 7]], by=4, comparison_on="payment_types", metric="rewards")
    make_violin_plots([filenames[i] for i in [3, 5, 7]], by=3, comparison_on="payment_types", metric="rewards")


def compare_stop_time():
    filenames = []
    for i in [25, 23, 20]:
        j = 25 - i
        for cd in [10, 30, 60]:
            filenames.append(f"{i}smart_t25_{j}freerider_{cd}+10")
    show_run_proportions(filenames, by=3, comparison_on="stop_time", metric="rewards")


def honest_vs_careful():
    h_name = "24honest_1saboteur"
    c_name = "24careful_s3_1saboteur"
    hdf = pd.read_csv(f"../data/behaviors/rewards/{h_name}.txt", header=None)
    cdf = pd.read_csv(f"../data/behaviors/rewards/{c_name}.txt", header=None)
    hdiff = hdf.iloc[:, :24].apply(np.mean, axis=1) - hdf.iloc[:, 24]
    cdiff = cdf.iloc[:, :24].apply(np.mean, axis=1) - cdf.iloc[:, 24]
    fig, axs = plt.subplots()
    axs.set_title("Reward Difference with Saboteur")
    line_hist(hdiff.values.flatten(), 1.5)
    line_hist(cdiff.values.flatten(), 1.5)
    axs.legend(["honest", "careful"])
    plt.show()


def items_collected_plot(filenames):
    fig, axs = plt.subplots()
    for filename in filenames:
        collected = pd.read_csv(f"../data/behaviors/items_collected/{filename}.txt", header=None)
        n_honest = int(re.search('[0-9]+', filename).group())
        line_hist(collected.iloc[:, :n_honest].values.flatten(), 1)
    axs.legend(filenames)
    axs.set_title("Items Collected Distribution")
    plt.show()


def rewards_plot(filenames):
    fig, axs = plt.subplots()
    for filename in filenames:
        rewards = pd.read_csv(f"../data/behaviors/rewards/{filename}.txt", header=None)
        n_honest = int(re.search('[0-9]+', filename).group())
        line_hist(rewards.iloc[:, :n_honest].values.flatten(), 1)
    axs.legend(filenames)
    axs.set_title("Honest Rewards Distribution")
    plt.show()


def show_run_difference(filenames, by=1, comparison_on="behaviors", metric="rewards"):
    nrows = len(filenames) // by
    ncols = by
    fig, axs = plt.subplots(nrows=nrows, ncols=ncols, sharey=True, sharex=True)
    print(axs)
    fig.set_size_inches(4 * ncols, 6 * nrows)
    for i, filename in enumerate(filenames):
        row = i // by
        col = i % by
        df = pd.read_csv(f"../data/{comparison_on}/{metric}/{filename}.txt", header=None)
        n_honest = int(re.search('[0-9]+', filename).group())
        n_bad = 25 - n_honest

        if nrows == 1 or ncols == 1:
            frame = axs[row] if ncols == 1 else axs[col]
        else:
            frame = axs[row, col]

        frame.set_title(filename)
        frame.set_ylabel(metric)
        frame.set_xlabel("run")
        run_difference_plot(df, frame, n_bad, n_honest)
    plt.show()


def run_difference_plot(df, ax, n_bad, n_honest):
    means = df.iloc[:, :n_honest].apply(np.mean, axis=1)
    means_bad = df.iloc[:, -n_bad:].apply(np.mean, axis=1)
    stds = df.iloc[:, :n_honest].apply(np.std, axis=1)
    stds_bad = df.iloc[:, -n_bad:].apply(np.std, axis=1)
    res = pd.concat([means, stds, means_bad, stds_bad], axis=1, keys=['mean', 'sd', 'mean_b', 'sd_b'])
    res = res.sort_values(by='mean')
    ax.errorbar(range(res.shape[0]), res['mean'], res['sd'], linestyle='None', marker='^', c="tab:blue")
    if n_bad > 0:
        ax.errorbar(range(res.shape[0]), res['mean_b'], res['sd_b'], linestyle='None', marker='^',
                    c=(1, 0, 0, 1))


def show_run_proportions(filenames, by=1, comparison_on="behaviors", metric="rewards"):
    nrows = len(filenames) // by
    ncols = by
    fig, axs = plt.subplots(nrows=nrows, ncols=ncols, sharey=True, sharex=True)
    print(axs)
    fig.set_size_inches(4 * ncols, 6 * nrows)
    for i, filename in enumerate(filenames):
        row = i // by
        col = i % by
        df = pd.read_csv(f"../data/{comparison_on}/{metric}/{filename}.txt", header=None)
        n_honest = int(re.search('[0-9]+', filename).group())
        n_bad = 25 - n_honest
        honest_name = re.search('[a-z]+', filename.split("_")[0]).group()
        bad_name = ""
        if n_bad > 0:
            try:
                bad_name = re.search('[a-z]+', filename.split("_")[2]).group()
            except IndexError:
                bad_name = re.search('[a-z]+', filename.split("_")[1]).group()
        colors = {"smart": "blue", "honest": "blue", "careful": "blue",
                  "saboteur": "red",
                  "smartboteur": "red",
                  "greedy": "green"}
        if nrows == 1 and ncols == 1:
            frame = axs
        elif nrows == 1 or ncols == 1:
            frame = axs[row] if ncols == 1 else axs[col]
        else:
            frame = axs[row, col]

        totals = df.apply(np.sum, axis=1)
        frame.set_title(f"{filename}, throughput = {round(np.mean(totals))}")
        frame.set_ylabel(f"proportion of {metric} (%)")
        frame.set_xlabel("run")

        means = df.iloc[:, :n_honest].apply(np.mean, axis=1) * 100 / totals
        means_bad = df.iloc[:, -n_bad:].apply(np.mean, axis=1) * 100 / totals
        stds = df.iloc[:, :n_honest].apply(np.std, axis=1) * 100 / totals
        stds_bad = df.iloc[:, -n_bad:].apply(np.std, axis=1) * 100 / totals
        res = pd.concat([means, stds, means_bad, stds_bad], axis=1, keys=['mean', 'sd', 'mean_b', 'sd_b'])
        res = res.sort_values(by='mean')
        frame.errorbar(range(res.shape[0]), res['mean'], res['sd'], linestyle='None', marker='^', c=colors[honest_name])
        if n_bad > 0:
            frame.errorbar(range(res.shape[0]), res['mean_b'], res['sd_b'], linestyle='None', marker='^',
                           c=colors[bad_name])
    plt.show()


def rewards_per_run(filename):
    df = pd.read_csv(f"../data/behaviors/rewards/{filename}.txt", header=None)
    n_honest = int(re.search('[0-9]+', filename).group())
    fig, axs = plt.subplots()
    for row in range(df.shape[0]):
        values = df.iloc[row, :n_honest].values.flatten()
        bins = np.arange(np.floor(np.min(values)), np.ceil(np.max(values)), 1)
        # plt.hist(values, bins=bins, fc=(1, 0, 0, 0.1))
        line_hist(values, 1, 0.1, color=(0.5, 0, 0, 0.1))
    plt.show()


def line_hist(values, precision, alpha=1.0, color=None):
    bins = np.arange(np.floor(np.min(values)), np.ceil(np.max(values)), precision)
    n, bins = np.histogram(values, bins=bins, density=True)
    plt.plot(bins[:-1], n, alpha=alpha, c=color)


def supply_demand_simulation():
    n_bots = 25
    demand = 0.3
    max_price = 3
    creditor_share = 0.5
    static_rewards = []
    supplies = range(1, n_bots + 1)
    active_rewards = []
    active_only_rewards = []
    for supply in supplies:
        n_active = supply
        reward_per_active = exponential_model(demand=demand * n_bots, max_price=max_price, supply=supply)
        static_reward = n_active * (creditor_share / (n_bots - 1)) * reward_per_active
        static_rewards.append(static_reward)
        active_reward = (((n_active - 1) / (n_bots - 1) * creditor_share) + 1 - creditor_share) * reward_per_active
        active_rewards.append(active_reward)
        active_only_rewards.append((1 - creditor_share) * reward_per_active)
    plt.plot(supplies, static_rewards)
    plt.plot(supplies, active_only_rewards)
    plt.plot(supplies, active_rewards)
    plt.axhline(y=max(static_rewards), color='r', linestyle='-')
    plt.legend(
        ["information", "foraging", "information + foraging", f"information max ={round(max(static_rewards), 2)}"])
    plt.title(f"creditor share = {creditor_share}, demand = {demand}")
    plt.xlabel("supply")
    plt.ylabel("reward")
    plt.show()


def make_violin_plots(filenames, by=1, comparison_on="behaviors", metric="rewards",
                      title="Individual reward share across subpopulations"):
    nrows = len(filenames) // by
    ncols = by
    fig, axs = plt.subplots(nrows=nrows, ncols=1, sharey=True, sharex=True)
    fig.set_size_inches(3 * ncols, 6 * nrows)
    x_name = "Experiment"
    y_name = "Proportion of total wealth (%)"
    hue_name = "behavior"

    for row in range(nrows):
        row_df = pd.DataFrame(columns=[x_name, hue_name, y_name])
        if nrows == 1:
            frame = axs
        else:
            frame = axs[row]
        frame.set_title(title)
        for col in range(ncols):
            filename = filenames[row * ncols + col]
            df = pd.read_csv(f"../data/{comparison_on}/{metric}/{filename}.txt", header=None)
            n_honest = int(re.search('[0-9]+', filename).group())
            honest_name = re.search('[a-z]+', filename.split("_")[0]).group()
            honest_name = name_conversion[honest_name]
            bad_name = re.search('[a-z]+', filename.split("_")[2]).group()
            bad_name = name_conversion[bad_name]
            n_bad = 25 - n_honest

            totals = df.apply(np.sum, axis=1)
            # print(totals)
            df_rel = df.div(totals, axis=0) * 100
            # means = df.iloc[:, :n_honest].apply(np.mean, axis=1) * 100 / totals
            honest_flat = pd.DataFrame(df_rel.iloc[:, :n_honest].to_numpy().flatten())
            bad_flat = pd.DataFrame(df_rel.iloc[:, -n_bad:].to_numpy().flatten())
            print(filename, stats.ranksums(honest_flat[:len(honest_flat) // 15], honest_flat[len(honest_flat) // 15:]))

            # means_bad = df.iloc[:, -n_bad:].apply(np.mean, axis=1) * 100 / totals
            # Draw a nested violinplot and split the violins for easier comparison

            goods = pd.DataFrame(np.full(honest_flat.shape, honest_name))
            bads = pd.DataFrame(np.full(honest_flat.shape, bad_name))
            honest_flat = pd.concat([honest_flat, goods], axis=1)
            bad_flat = pd.concat([bad_flat, bads], axis=1)
            final_df = pd.concat([honest_flat, bad_flat])
            final_df.columns = [y_name, hue_name]
            final_df[x_name] = f"{n_honest} {honest_name} vs {n_bad} {bad_name}"
            row_df = pd.concat([row_df, final_df])
        row_df.index = [i for i in range(row_df.shape[0])]
        temp = pd.DataFrame(row_df.to_dict())
        sns.violinplot(data=temp, x=x_name, y=y_name, hue=hue_name,
                       split=True, inner="quart", linewidth=2, ax=frame, palette=palette, cut=0)

    plt.show()


def make_boxplots(filenames, by=1, comparison_on="behaviors", metric="rewards",
                  title="Individual reward share across subpopulations"):
    nrows = len(filenames) // by
    ncols = by
    x_name = "Experiment"
    y_name = "Proportion of total wealth (%)"
    hue_name = "behavior"

    for row in range(nrows):
        fig, axs = plt.subplots(1, ncols, sharey=True)
        fig.suptitle(title)
        fig.supxlabel(x_name)
        fig.supylabel(y_name)
        fig.set_size_inches(3 * ncols, 6)
        for col in range(ncols):
            filename = filenames[row * ncols + col]
            df = pd.read_csv(f"../data/{comparison_on}/{metric}/{filename}.txt", header=None)
            n_honest = int(re.search('[0-9]+', filename).group())
            honest_name = re.search('[a-z]+', filename.split("_")[0]).group()
            honest_name = name_conversion[honest_name]
            bad_name = re.search('[a-z]+', filename.split("_")[2]).group()
            bad_name = name_conversion[bad_name]
            n_bad = 25 - n_honest

            totals = df.apply(np.sum, axis=1)
            df_rel = df.div(totals, axis=0) * 100
            honest_flat = pd.DataFrame(df_rel.iloc[:, :n_honest].to_numpy().flatten())
            bad_flat = pd.DataFrame(df_rel.iloc[:, -n_bad:].to_numpy().flatten())
            print(filename, stats.ranksums(honest_flat, bad_flat))

            goods = pd.DataFrame(np.full(honest_flat.shape, honest_name))
            bads = pd.DataFrame(np.full(honest_flat.shape, bad_name))
            honest_flat = pd.concat([honest_flat, goods], axis=1)
            bad_flat = pd.concat([bad_flat, bads], axis=1)
            final_df = pd.concat([honest_flat, bad_flat])
            final_df.columns = [y_name, hue_name]
            final_df[x_name] = f"{n_honest} {honest_name} vs {n_bad} {bad_name}"
            axs[col].set_title(chr(col + 65), fontweight="bold")
            sns.boxplot(data=final_df, x=x_name, y=y_name, hue=hue_name, linewidth=2, ax=axs[col], palette=palette).set(
                xlabel=None, ylabel=None)
        plt.show()


def items_collected_violin_plot(df, frame, n_good, n_bad, good_name="naive", bad_name="saboteur", xlabel="all",
                                title=None):
    honest_flat = pd.DataFrame(df.iloc[:, :n_good].to_numpy().flatten())
    bad_flat = pd.DataFrame(df.iloc[:, n_good:n_good + n_bad].to_numpy().flatten())

    goods = pd.DataFrame(np.full(honest_flat.shape, good_name))
    bads = pd.DataFrame(np.full(bad_flat.shape, bad_name))
    honest_flat = pd.concat([honest_flat, goods], axis=1)
    bad_flat = pd.concat([bad_flat, bads], axis=1)
    final_df = pd.concat([honest_flat, bad_flat])
    final_df.columns = ["items collected", "behavior"]
    final_df["run"] = xlabel
    split = n_bad > 0 and n_good > 0
    sns.violinplot(data=final_df, x="run", y="items collected", hue="behavior",
                   split=split, inner="quart", linewidth=2, ax=frame, palette=palette,
                   bw=0.275)
    if title:
        frame.set_title(title, fontweight="bold")
    frame.set(xlabel=None, ylabel=None)


def items_collected_boxplot(df, frame, n_good, n_bad, good_name="naive", bad_name="saboteur", xlabel="all", title=None):
    honest_flat = pd.DataFrame(df.iloc[:, :n_good].to_numpy().flatten())
    bad_flat = pd.DataFrame(df.iloc[:, n_good:n_good + n_bad].to_numpy().flatten())

    goods = pd.DataFrame(np.full(honest_flat.shape, good_name))
    bads = pd.DataFrame(np.full(bad_flat.shape, bad_name))
    honest_flat = pd.concat([honest_flat, goods], axis=1)
    bad_flat = pd.concat([bad_flat, bads], axis=1)
    final_df = pd.concat([honest_flat, bad_flat])
    final_df.columns = ["items collected", "behavior"]
    final_df["run"] = xlabel
    sns.boxplot(data=final_df, x="run", y="items collected", hue="behavior", linewidth=2,
                ax=frame, palette=palette)
    if title:
        frame.set_title(title, fontweight="bold")
    frame.set(xlabel=None, ylabel=None)


def test_angles():
    df_all = pd.DataFrame(
        [[1, 1, Location.FOOD, 0], [2, 4, Location.NEST, 0], [2, 5, Location.NEST, 0], [1, 100, Location.FOOD, 0],
         [4, 359, Location.FOOD, 0]], columns=["seller", "angle", "location", "alike"])
    angle_window = 5
    total_amount = 0.5
    for location in Location:
        df = df_all[df_all["location"] == location]
        df["alike"] = df.apply(func=lambda row: pd.DataFrame(
            [(df.iloc[:, 1] - row[1]) % 360,
             (row[1] - df.iloc[:, 1]) % 360]).
                               apply(min, axis=0).
                               sum(),
                               axis=1)
        # pd.DataFrame([(df.iloc[:, 1] - row[1]) % 360, (row[1] - df.iloc[:, 1]) % 360]).apply(min, axis=1).sum()
        # print(pd.DataFrame(
        #     [(df.iloc[:, 1] - df.iloc[1, 1]) % 360,
        #      (df.iloc[1, 1] - df.iloc[:, 1]) % 360]))
        # print(df)
        sellers_to_alike = df.groupby("seller").sum()
        print(sellers_to_alike)
        sellers_to_alike["alike"] = sellers_to_alike["alike"].sum() - sellers_to_alike["alike"]
        sellers_to_alike = sellers_to_alike.to_dict()["alike"]
        print(sellers_to_alike)
    # total_shares = sum(sellers_to_alike.values())
    # mapping = {seller: total_amount * sellers_to_alike[seller] / total_shares for seller in sellers_to_alike}
    # print(mapping)


def test_timedev():
    sorted_transactions = [[1, 1], [2, 4], [3, 4], [1, 7], [5, 12]]
    timestep = 20
    total_amount = 0.5
    sorted_transactions.append([-1, timestep])
    df = pd.DataFrame(sorted_transactions, columns=["seller", "time"])
    df["dt"] = df["time"].diff().shift(-1) + 1
    df = df[:-1]
    df["score"] = 1 / df["dt"]
    df["share"] = total_amount * df["score"] / df["score"].sum()
    mapping = df.groupby("seller").sum().to_dict()["share"]
    print(df)

    print(mapping)


def thesis_plots():
    # Chapter 8 - Section 1
    # chap8_1()

    # Chapter 8 - Section 2
    # chap8_2()

    # Chapter 9 - Section 1
    # filenames = ["24smart_t25_1smartboteur_SoR_50",
    #              "22smart_t25_3smartboteur_SoR_50",
    #              "20smart_t25_5smartboteur_SoR_50"]
    # make_violin_plots(filenames, by=3, comparison_on="saboteur_comp",
    #                   title="Wealth Repartition, Reward Share Transactions, Fixed Reward")
    # filenames = ["24smart_t25_1smartboteur_SoR_50_RTmarket",
    #              "22smart_t25_3smartboteur_SoR_50_RTmarket",
    #              "20smart_t25_5smartboteur_SoR_50_RTmarket"]
    # make_violin_plots(filenames, by=3, comparison_on="saboteur_comp",
    #                   title="Wealth Repartition, Reward Share Transactions, Round-trip Duration Reward")
    #
    # filenames = ["24smart_t25_1smartgreedy_windowdev_50_RTmarket",
    #              "22smart_t25_3smartgreedy_windowdev_50_RTmarket",
    #              "20smart_t25_5smartgreedy_windowdev_50_RTmarket"]
    # make_violin_plots(filenames, by=3, comparison_on="saboteur_comp",
    #                   title=" Wealth Repartition, Reward Share Transactions, Round-trip Duration Reward")
    #
    filenames = ["24smart_t25_1smartboteur_vouchwindowdev_50_fixedmarket",
                 "22smart_t25_3smartboteur_vouchwindowdev_50_fixedmarket",
                 "20smart_t25_5smartboteur_vouchwindowdev_50_fixedmarket"]
    make_violin_plots(filenames, by=3, comparison_on="saboteur_comp", metric="rewards",
                      title="Wealth Repartition, Window + Vouch, Fixed Reward")

    # Final Presentation

    # fig, axs = plt.subplots(1, 4, sharey=True)
    # fig.set_size_inches(12, 6)
    # fig.suptitle("Swarm Performance")
    # fig.supylabel("Number of Items Collected")
    # fig.supxlabel("Experiment")
    # df = pd.read_csv("../data/behaviors/items_collected/25honest.txt", header=None)
    # items_collected_violin_plot(df, axs[2], 25, 0, xlabel="25 naive")
    # df = pd.read_csv("../data/behaviors/items_collected/24honest_1saboteur.txt", header=None)
    # items_collected_violin_plot(df, axs[0], 24, 1, xlabel="24 naive vs 1 saboteur")
    # df = pd.read_csv("../data/behaviors/items_collected/25smart_t25.txt", header=None)
    # items_collected_violin_plot(df, axs[3], 25, 0, xlabel="25 smart", good_name="smart", bad_name="smartboteur")
    # df = pd.read_csv("../data/saboteur_comp/items_collected/24smart_t25_1smartboteur_SoR_50.txt", header=None)
    # items_collected_violin_plot(df, axs[1], 24, 1, xlabel="24 smart vs 1 smartboteur", good_name="smart", bad_name="smartboteur")
    # plt.show()
    #
    # fig, axs = plt.subplots(1, 3, sharey=True)
    # fig.set_size_inches(12, 6)
    # fig.suptitle("Swarm Performance")
    # fig.supylabel("Number of Items Collected")
    # fig.supxlabel("Experiment")
    # df = pd.read_csv("../data/saboteur_comp/items_collected/24smart_t25_1smartboteur_SoR_50.txt", header=None)
    # items_collected_violin_plot(df, axs[0], 24, 1, xlabel="24 smart vs 1 smartboteur")
    # df = pd.read_csv("../data/saboteur_comp/items_collected/22smart_t25_3smartboteur_SoR_50.txt", header=None)
    # items_collected_violin_plot(df, axs[1], 24, 1, xlabel="22 smart vs 3 smartboteur")
    # df = pd.read_csv("../data/saboteur_comp/items_collected/20smart_t25_5smartboteur_SoR_50.txt", header=None)
    # items_collected_violin_plot(df, axs[2], 24, 1, xlabel="20 smart vs 5 smartboteur")
    # plt.show()

    # df =pd.read_csv("../data/saboteur_comp/rewards/20smart_t25_5smartboteur_SoR_50_RTmarket.txt")
    # x = df.iloc[:, :20].to_numpy().flatten()
    # y = df.iloc[:, 20:].to_numpy().flatten()
    # res = mannwhitneyu(x, y, alternative='greater')
    # print(res)

    fig, axs = plt.subplots(1, 2, sharey=True)
    fig.set_size_inches(6, 6)
    fig.suptitle("Swarm Performance")
    fig.supylabel("Number of Items Collected")
    fig.supxlabel("Experiment")
    df = pd.read_csv("../data/saboteur_comp/items_collected/24smart_t25_1smartboteur_SoR_50.txt", header=None)
    items_collected_violin_plot(df, axs[0], 24, 1, xlabel="24 smart vs 1 smartboteur")
    df = pd.read_csv("../data/saboteur_comp/items_collected/24smart_t25_1smartboteur_vouchwindowdev_50_fixedmarket.txt",
                     header=None)
    items_collected_violin_plot(df, axs[1], 24, 1, xlabel="24 smart vs 1 smartboteur")
    plt.show()


def chap8_2():
    filenames = ["../data/behaviors/items_collected/25honest.txt",
                 "../data/behaviors/items_collected/25smart_t25.txt",
                 "../data/behaviors/items_collected/25careful.txt"]
    robot_name = ["Naive", "Smart", "Careful"]
    fig, axs = plt.subplots(1, 3, sharey=True)
    fig.set_size_inches(10, 6)
    fig.suptitle("Comparing Honest Behaviors")
    fig.supylabel("Number of Items Collected")
    fig.supxlabel("Behavior")
    for i, file in enumerate(filenames):
        df = pd.read_csv(file, header=None)
        general_boxplot_data = df.values.flatten()
        sns.violinplot(x=[robot_name[i] for e in general_boxplot_data], y=general_boxplot_data, ax=axs[i], linewidth=2,
                       bw=.3)
    plt.show()
    robot_name = ["Smart", "Careful"]
    filenames = [
        "../data/saboteur_comp/items_collected/24smart_t25_1smartboteur_SoR_50.txt",
        "../data/saboteur_comp/items_collected/24smart_t25_1smartboteur_SoR_50_RTmarket.txt"]
    for i, file in enumerate(filenames):
        df = pd.read_csv(file, header=None)
        fig, axs = plt.subplots(1, 2, sharey=True)
        fig.suptitle(f"Performance of {robot_name[i]} Swarm with 1 Saboteur")
        fig.supylabel("Number of Items Collected")
        fig.supxlabel("Run Considered")
        print(np.median(df.to_numpy().flatten()))
        items_collected_violin_plot(df, axs[0], 24, 1, good_name=robot_name[i].lower())
        run_difference_plot(df, axs[1], 1, 24)
        plt.show()
    # x = pd.read_csv(filenames[0], header=None).to_numpy().flatten()
    # y = pd.read_csv(filenames[1], header=None).to_numpy().flatten()
    # print(len(x), len(y))
    # print(wilcoxon(x=x, y=y))


def chap8_1():
    filename = "../data/behaviors/items_collected/25honest.txt"
    df = pd.read_csv(filename, header=None)
    general_boxplot_data = df.values.flatten()
    fig, axs = plt.subplots(1, 2, sharey=True, gridspec_kw={'width_ratios': [1, 4]})
    fig.set_size_inches(10, 6)
    sns.violinplot(x=["all" for e in general_boxplot_data], y=general_boxplot_data, ax=axs[0], bw=.3, linewidth=2)
    run_difference_plot(df, axs[1], 0, 25)
    # run_difference_plot(pd.read_csv("../data/behaviors/items_collected/24honest_1saboteur.txt", header=None), axs[2], 1, 24)
    fig.suptitle("Performance of Naïve Swarm")
    fig.supylabel("Number of Items Collected")
    fig.supxlabel("Run Considered")
    plt.show()
    df = pd.read_csv("../data/behaviors/items_collected/24honest_1saboteur.txt", header=None)
    fig, axs = plt.subplots(1, 2, sharey=True, gridspec_kw={'width_ratios': [1, 4]})
    fig.set_size_inches(10, 6)
    fig.suptitle("Performance of Naïve Swarm with 1 Saboteur")
    fig.supylabel("Number of Items Collected")
    fig.supxlabel("Run Considered")
    items_collected_violin_plot(df, axs[0], 24, 1)
    run_difference_plot(df, axs[1], 1, 24)
    plt.show()


def test_windowdev():
    pd.options.mode.chained_assignment = None
    angle_window = 30
    total_amount = 0.5
    transactions = [[1, 1, Location.NEST, 0], [2, 4, Location.NEST, 0],
                    [2, 5, Location.NEST, 0], [3, 100, Location.NEST, 0],
                    [4, 359, Location.NEST, 0]]
    df_all = pd.DataFrame(transactions, columns=["seller", "angle", "location", "alike"])
    final_mapping = {}
    for location in Location:
        df = df_all[df_all["location"] == location]
        df.loc[:, "alike"] = df.apply(func=lambda row: (((df.loc[:, "angle"] - row[1]) % 360) < angle_window).sum()
                                                       + (((row[1] - df.loc[:,
                                                                     "angle"]) % 360) < angle_window).sum() - 1,
                                      axis=1)
        sellers_to_alike = df.groupby("seller").sum().to_dict()["alike"]
        mapping = {seller: sellers_to_alike[seller] for seller in sellers_to_alike}
        for seller in mapping:
            if seller in final_mapping:
                final_mapping[seller] += mapping[seller]
            else:
                final_mapping[seller] = mapping[seller]
    total_shares = sum(final_mapping.values())

    for seller in final_mapping:
        final_mapping[seller] = final_mapping[seller] * total_amount / total_shares
    print(final_mapping)


def test_np_windowdev():
    angle_window = 30
    total_amount = 0.5
    transactions = [[1, 1, Location.NEST, 0], [2, 4, Location.NEST, 0],
                    [2, 5, Location.NEST, 0], [3, 100, Location.NEST, 0],
                    [4, 359, Location.NEST, 0]]
    df_all = np.array(transactions)
    angle_window = 30
    final_mapping = {}
    for location in Location:
        df = df_all[df_all[:, 2] == location]
        if df.shape[0] == 0:
            continue
        df[:, 3] = np.apply_along_axis(func1d=lambda row: (((df[:, 1] - row[1]) % 360) < angle_window).sum()
                                                          + (((row[1] - df[:, 1]) % 360) < angle_window).sum() - 1,
                                       axis=1, arr=df)
        mapping = {seller: 0 for seller in df[:, 0]}
        for row in df:
            mapping[row[0]] += row[3]

        for seller in mapping:
            if seller in final_mapping:
                final_mapping[seller] += mapping[seller]
            else:
                final_mapping[seller] = mapping[seller]

    total_shares = sum(final_mapping.values())
    for seller in final_mapping:
        final_mapping[seller] = final_mapping[seller] * (total_amount) / total_shares
    print(final_mapping)


def paper_plots():
    sns.set_style("whitegrid")
    # fig, axs = plt.subplots(1, 4, sharey=True)
    # fig.set_size_inches(12, 6)
    # fig.suptitle("Swarm Performance")
    # fig.supylabel("Number of Items Collected")
    # fig.supxlabel("Experiment")
    #
    # df = pd.read_csv("../data/correlation/items_collected/25naive_0saboteur_nostake.txt", header=None)
    # items_collected_violin_plot(df, axs[0], 25, 0, xlabel="25 naive")
    #
    # df = pd.read_csv("../data/correlation/items_collected/24naive_1saboteur_nostake.txt", header=None)
    # items_collected_violin_plot(df, axs[1], 24, 1, xlabel="24 naive vs 1 saboteur")
    #
    # df = pd.read_csv("../data/correlation/items_collected/25smart_t25_0smartboteur_nostake.txt", header=None)
    # items_collected_violin_plot(df, axs[2], 25, 0, xlabel="25 sceptical", good_name="sceptical", bad_name="scaboteur")
    #
    # df = pd.read_csv("../data/correlation/items_collected/24smart_t25_1smartboteur_nostake.txt", header=None)
    # items_collected_violin_plot(df, axs[3], 24, 1, xlabel="24 sceptical vs 1 scaboteur", good_name="sceptical", bad_name="scaboteur")

    # df = pd.read_csv("../data/behaviors/items_collected/25smart_t25_0smartboteur_weighted.txt", header=None)
    # items_collected_violin_plot(df, axs[4], 25, 0, xlabel="25 smart weighted", good_name="smart", bad_name="smartboteur")
    #
    # df = pd.read_csv("../data/behaviors/items_collected/24smart_t25_1smartboteur_weighted.txt", header=None)
    # items_collected_violin_plot(df, axs[5], 24, 1, xlabel="24 smart vs 1 smartboteur weighted", good_name="smart",
    #                             bad_name="smartboteur")
    # plt.show ()

    fig, axs = plt.subplots(1, 4, sharey=True)
    fig.set_size_inches(12, 6)
    fig.suptitle("Swarm Performance")
    fig.supylabel("Number of Items Collected")
    fig.supxlabel("Experiment")
    df = pd.read_csv("../data/correlation/items_collected/25naive_0saboteur_nostake.txt", header=None)
    items_collected_boxplot(df, axs[0], 25, 0, xlabel="25 naive", title="A")

    df = pd.read_csv("../data/correlation/items_collected/24naive_1saboteur_nostake.txt", header=None)
    items_collected_boxplot(df, axs[1], 24, 1, xlabel="24 naive vs 1 saboteur", title="B")

    df = pd.read_csv("../data/correlation/items_collected/25smart_t25_0smartboteur_nostake.txt", header=None)
    items_collected_boxplot(df, axs[2], 25, 0, xlabel="25 sceptical", good_name="sceptical", bad_name="scaboteur",
                            title="C")

    df = pd.read_csv("../data/correlation/items_collected/24smart_t25_1smartboteur_nostake.txt", header=None)
    items_collected_boxplot(df, axs[3], 24, 1, xlabel="24 sceptical vs 1 scaboteur", good_name="sceptical",
                            bad_name="scaboteur", title="D")

    # df = pd.read_csv("../data/behaviors/items_collected/25smart_t25_0smartboteur_weighted.txt", header=None)
    # items_collected_boxplot(df, axs[4], 25, 0, xlabel="25 smart weighted", good_name="smart",
    #                             bad_name="scaboteur")
    #
    # df = pd.read_csv("../data/behaviors/items_collected/24smart_t25_1smartboteur_weighted.txt", header=None)
    # items_collected_boxplot(df, axs[5], 24, 1, xlabel="24 smart vs 1 smartboteur weighted", good_name="smart",
    #                             bad_name="smartboteur")
    plt.show()

    filenames = ["24smart_t25_1smartboteur_nostake",
                 "22smart_t25_3smartboteur_nostake",
                 "20smart_t25_5smartboteur_nostake"]
    # make_violin_plots(filenames, by=3, comparison_on="correlation", title="Wealth Repartition - Outlier Penalisation")
    make_boxplots(filenames, by=3, comparison_on="correlation",
                  title="Wealth Repartition - Outlier Penalisation")

    filenames = ["24smart_t25_1smartboteur_windowvouch",
                 "22smart_t25_3smartboteur_windowvouch",
                 "20smart_t25_5smartboteur_windowvouch"]
    # make_violin_plots(filenames, by=3, comparison_on="correlation", metric="rewards", title="Wealth Repartition - Outlier Penalisation with Staking")
    make_boxplots(filenames, by=3, comparison_on="correlation", metric="rewards",
                  title="Wealth Repartition - Outlier Penalisation with Staking")


def to_reward_wealth_proportion(df):
    totals = df.apply(np.sum, axis=1)
    df_rel = df.div(totals, axis=0) * 100
    return df_rel


def to_long(df, N_HONEST, x_name, y_name, hue_name, honest_name, saboteur_name):
    df.columns = [str(i + 1) for i in range(25)]
    df[x_name] = df.index
    df = pd.melt(df, id_vars=[x_name], value_vars=[str(i + 1) for i in range(25)], var_name="id", value_name=y_name)
    df[hue_name] = honest_name
    df.loc[df["id"].astype(int) > N_HONEST, hue_name] = saboteur_name
    return df


def reward_evolution():
    N_RUNS = 32
    N_HONEST = 20
    N_SABOTEURS = 25 - N_HONEST
    x_name = "time"
    y_name = "Individual weatlh ($)"
    hue_name = "behavior"
    honest_name = "sceptical"
    saboteur_name = "scaboteur"
    dfs = []
    for i in range(N_RUNS):
        df = pd.read_csv(
            f"../data/correlation/reward_evolution/{N_HONEST}smart_t25_{N_SABOTEURS}smartboteur_nostake/{i}.txt",
            header=None, index_col=0)
        # df = to_reward_wealth_proportion(df)
        df = df.iloc[::10, :]
        df = to_long(df, N_HONEST, x_name, y_name, hue_name, honest_name, saboteur_name)
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)
    print(df)
    plt.suptitle("A", fontweight="bold")
    plt.title(f"Outlier penalisation - {N_HONEST} {honest_name} vs {N_SABOTEURS} {saboteur_name}")
    sns.lineplot(data=df, x=x_name, y=y_name, hue=hue_name, palette=palette)
    plt.show()


def correlation_plot(filename, directory, suptitle=None):
    n_honest = int(re.search('[0-9]+', filename).group())
    n_bad = 25 - n_honest
    honest_name = re.search('[a-z]+', filename.split("_")[0]).group()
    bad_name = re.search('[a-z]+', filename.split("_")[2]).group()
    rewards = pd.read_csv(f"{directory}rewards/{filename}", header=None)
    items_collected = pd.read_csv(f"{directory}items_collected/{filename}", header=None)
    # rewards = rewards - 0.5*items_collected
    wealth = to_reward_wealth_proportion(rewards)
    drifts = pd.read_csv(f"{directory}drifts/{filename}", header=None)
    drifts = drifts.applymap(abs)
    y = wealth.iloc[:, :n_honest].to_numpy().flatten()
    x = drifts.iloc[:, :n_honest].to_numpy().flatten()
    sns.regplot(x=x, y=y, scatter=True, truncate=True,
                line_kws={"color": "darkblue"}, scatter_kws={"alpha": 0.2, "linewidth": 0})
    plt.title(
        f"{n_honest} sceptical vs {n_bad} scaboteurs with staking")  # - pearson={round(np.corrcoef(x, y)[0, 1], 2)}
    plt.xlabel("drift")
    plt.ylabel("Proportion of total wealth(%)")
    if suptitle:
        plt.suptitle(suptitle, fontweight="bold")
    plt.show()


# filenames = [
#     "25smart_t25_0smartboteur_windowvouch.txt",
#     "20smart_t25_5smartboteur_windowvouch.txt",
#     # "22smart_t25_3smartboteur_windowvouch.txt",
#     # "24smart_t25_1smartboteur_windowvouch.txt",
# ]


def correlation_plots():
    for i, filename in enumerate(filenames):
        correlation_plot(filename, "../data/correlation/", chr(i + 65))


def total_items_collected_boxplot(filenames, ncol=9, comparison_on="scaboteur_rotation",
                                  title=""):
    nrows = len(filenames) // ncol
    fig, axs = plt.subplots(nrows, ncol, sharey=True)
    size = np.array([3 * ncol, 14 * nrows])
    fig.set_size_inches(tuple(size * 0.35))
    fig.suptitle(title)
    fig.supylabel("Number of items collected")
    fig.supxlabel("Scaboteur 'lie angle' (in degrees)")
    for i, (filename, ax) in enumerate(zip(filenames, axs.flatten())):
        col = i % ncol
        name1 = re.search('[a-z]+', filename.split("_")[0]).group()
        name2 = re.search('[a-z]+', filename.split("_")[2]).group()
        n1 = int(re.search('[0-9]+', filename).group())
        n2 = 25 - n1
        df = pd.read_csv(f'../data/{comparison_on}/items_collected/{filename}.txt', header=None).to_numpy()
        items_collected = np.sum(df, axis=1)
        angle = 10 * (col + 0)
        sns.boxplot(x=[angle for _ in items_collected], y=items_collected, ax=ax, linewidth=2)
        if col == 0:
            ax.set(ylabel=f'{n1} {name1} vs {n2} {name2}')
        ax.set_title(chr(i + 65), fontweight="bold")
    plt.ylim(bottom=0)
    plt.show()


def multi_line_boxplots(filenames, ncol=9, comparison_on="scaboteur_rotation", metric="rewards", title=""):
    nrows = len(filenames) // ncol
    fig, axs = plt.subplots(nrows, ncol, sharey='row')
    size = np.array([5 * ncol, 12*nrows])
    fig.set_size_inches(tuple(size*0.35))
    fig.suptitle(title)
    fig.supylabel("Proportion of total wealth (%)")
    fig.supxlabel("Scaboteur 'lie angle' (in degrees)")
    for i, (filename, ax) in enumerate(zip(filenames, axs.flatten())):
        col = i % ncol
        name1 = re.search('[a-z]+', filename.split("_")[0]).group()
        name2 = re.search('[a-z]+', filename.split("_")[2]).group()
        n1 = int(re.search('[0-9]+', filename).group())
        n2 = 25 - n1
        raw_data = pd.read_csv(f'../data/{comparison_on}/{metric}/{filename}.txt', header=None)
        raw_data = raw_data.apply(lambda row: row/row.sum(), axis=1)
        shares1 = pd.DataFrame(raw_data.iloc[:, :n1].to_numpy().flatten())
        shares1['name'] = name1
        shares2 = pd.DataFrame(raw_data.iloc[:, n1:].to_numpy().flatten())
        shares2['name'] = name2
        df = pd.concat([shares1, shares2], axis=0).rename(columns={0: 'reward_share'})
        df['angle'] = 10 * (col + 1)
        sns.boxplot(data=df,  x='angle', y='reward_share', hue='name', ax=ax, palette=palette, linewidth=2) \
            .set(xlabel='', ylabel='')
        sns.despine(fig, ax, trim=True)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend_.remove()
        if col == 0:
            ax.set(ylabel=f'{n1} {name1} vs {n2} {name2}')
        ax.set_title(chr(i + 65), fontweight="bold")
        # ax.legend(loc="upper center")
    fig.legend(handles, labels)
    plt.ylim(bottom=0)
    plt.show()


def separate_line_boxplots(filenames, x_values=None, comparison_on="scaboteur_rotation", metric="rewards", title=""):
    nrows = len(filenames)
    fig, axs = plt.subplots(nrows, 1)
    size = np.array([3.5 * len(filenames[0]), 12*nrows])
    fig.set_size_inches(tuple(size*0.35))
    fig.suptitle(title)
    fig.supylabel("Proportion of total wealth (%)")
    fig.supxlabel("Scaboteur 'lie angle' (in degrees)")
    for row, ax in zip(filenames, axs):
        dataframes = []
        for i, filename in enumerate(row):
            name1 = re.search('[a-z]+', filename.split("_")[0]).group()
            name2 = re.search('[a-z]+', filename.split("_")[2]).group()
            n1 = int(re.search('[0-9]+', filename).group())
            n2 = 25 - n1
            raw_data = pd.read_csv(f'../data/{comparison_on}/{metric}/{filename}.txt', header=None)
            raw_data = raw_data.apply(lambda row: 100*row/row.sum(), axis=1)
            shares1 = pd.DataFrame(raw_data.iloc[:, :n1].to_numpy().flatten())
            shares1['name'] = name1
            shares2 = pd.DataFrame(raw_data.iloc[:, n1:].to_numpy().flatten())
            shares2['name'] = name2
            df = pd.concat([shares1, shares2], axis=0).rename(columns={0: 'reward_share'})
            df['angle'] = 10 * (i + 1)
            dataframes.append(df)
        data = pd.concat(dataframes)
        sns.boxplot(data=data,  x='angle', y='reward_share', hue='name', ax=ax, palette=palette, linewidth=2) \
            .set(xlabel='', ylabel='')
        handles, labels = ax.get_legend_handles_labels()
        ax.legend_.remove()
        ax.set_title(f'{n1} {name1} vs {n2} {name2}')
    fig.legend(handles, labels)
    plt.ylim(bottom=-1)
    plt.show()


def scaboteur_rotation(n_scaboteurs=(1, 3)):
    filenames = [
        [f'{25 - n_scaboteur}sceptical_t25_{n_scaboteur}scaboteur_stake_rotation_{i}' for i in range(0, 91, 10)]
        for n_scaboteur in n_scaboteurs
    ]
    # make_boxplots(filenames,
    #               by=9,
    #               comparison_on="scaboteur_rotation",
    #               metric="rewards",
    #               title="Wealth Repartition - Outlier Penalisation with Staking - 10 to 90 Degree Rotation of Scaboteur Vector")
    print(filenames)
    total_items_collected_boxplot([filename for row in filenames for filename in row],
                                  ncol=10,
                                  comparison_on="scaboteur_rotation",
                                  title="Swarm Performance Comparison: Varying Scaboteur Lie Intensity")
    separate_line_boxplots([row[1:] for row in filenames],
                           x_values=None,
                           comparison_on="scaboteur_rotation",
                           metric="rewards",
                           title="Scaboteur Penalisation Comparison: Varying Scaboteur Lie Intensity")


def penalisation_vs_stake_items_collected(n_scaboteurs=3):
    angles = range(0, 91, 10)
    filenames_stake = [
        f'{25 - n_scaboteurs}sceptical_t25_{n_scaboteurs}scaboteur_stake_rotation_{i}' for i in angles
    ]
    filenames_nopenalisation = [
        f'{25 - n_scaboteurs}sceptical_t25_{n_scaboteurs}scaboteur_nopenalisation_rotation_{i}' for i in angles
    ]
    to_concat = []
    for angle, stake_file, nopenalisation_file in zip(angles, filenames_stake, filenames_nopenalisation):
        stake = pd.read_csv(f'../data/scaboteur_rotation/items_collected/{stake_file}.txt', header=None)
        no_pen = pd.read_csv(f'../data/scaboteur_rotation/items_collected/{nopenalisation_file}.txt', header=None)
        stake_items_per_run = pd.DataFrame(stake.apply(np.sum, axis=1), columns=['Number of items collected'])
        nopenalisation_items_per_run = pd.DataFrame(no_pen.apply(np.sum, axis=1), columns=['Number of items collected'])
        stake_items_per_run['penalisation'] = 'with'
        nopenalisation_items_per_run['penalisation'] = 'without'
        both = pd.concat([stake_items_per_run, nopenalisation_items_per_run])
        both["Scaboteur 'lie angle' (in degrees)"] = angle
        to_concat.append(both)
    df = pd.concat(to_concat)
    size = np.array([3.5 * len(filenames_stake), 12])
    fig = plt.figure(num=0, figsize=size*0.35)
    sns.boxplot(data=df,
                x="Scaboteur 'lie angle' (in degrees)",
                y='Number of items collected', hue='penalisation',
                linewidth=2)\
        .set(title=f"Swarm Performance Comparison: With or Without Penalisation Scheme ({n_scaboteurs} scaboteur{'s' if n_scaboteurs > 1 else ''})")
    plt.ylim(bottom=-1)
    plt.show()


def after_transitory_phase():
    withoutpen = pd.read_csv("../data/new/items_evolution/nopen.csv", converters={"items_list": pd.eval})
    withpen = pd.read_csv('../data/new/items_evolution/pen.csv', converters={"items_list": pd.eval})
    # withoutpen = pd.read_csv("../data/new/items_evolution/nopen.csv", header=None)
    # withpen = pd.read_csv('../data/new/items_evolution/pen.csv', header=None)
    withpen['penalisation'] = 'with'
    withoutpen['penalisation'] = 'without'
    df = pd.concat([withoutpen, withpen]).sort_values('penalisation')
    df['Number of items collected (after first half of simulation)'] = df.iloc[:, :25].apply(lambda row: row.sum(), axis=1)
    df["Scaboteur 'lie angle' (in degrees)"] = 0
    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(3, 6)
    sns.boxplot(data=df, x="Scaboteur 'lie angle' (in degrees)", y='Number of items collected (after first half of simulation)', hue='penalisation', ax=ax)
    plt.title("Swarm Performance: With or Without Penalisation, Ignoring First 7500 Steps")
    plt.ylim(0, None)
    plt.show()


if __name__ == '__main__':
    # metric,mode=parse_args()
    # myboxplots()
    # myttest(data_folder="../data/all/",compare="")
    # myanovatest()
    # sidebyside_boxplots()
    # plot_evolution(compare="g")
    # evolution_boxplot0()
    # after_transitory_phase()
    # boxplot_evo_pen_lie()
    boxplot_repu()
    pass