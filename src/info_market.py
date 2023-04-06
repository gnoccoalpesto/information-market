import time
import datetime
import pandas as pd
from multiprocessing import Pool
from pathlib import Path
from os.path import join, exists, isfile
from os import listdir, system
from sys import argv
import argparse
# from json.decoder import JSONDecodeError

import config as CONFIG_FILE
from controllers.main_controller import MainController, Configuration
from controllers.view_controller import ViewController
# import data_analysis


### UTILITIES ######################################################################
# #TODO
# def parse_args():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-a', '--all',action='store_true',required=False,
#                     help='use all files from a single folder')
#     args=parser.parse_args()
#     if args.all:
#         select_all=True
#     return select_all


def check_filename_existence(output_directory,metric,filename):
    new_filename = filename
    if exists(join(output_directory, metric, filename)):
        exist_count = len([f for f in Path(join(output_directory, metric))\
            .iterdir() if f.name.startswith(new_filename.replace(".csv", ""))])
        new_filename = new_filename.replace(".csv", f"_{exist_count}.csv")
    return new_filename


def generate_filename(config:Configuration,):
    filename = config.value_of("data_collection")["filename"]
    return filename#.split(".csv")[0].replace(".","")+".csv"

    
####################################################################################

def main():
    try:
        filenames=[]
        for p in argv[1:]:
            if isfile(p):
                config = Configuration(config_file=p)
                if config.value_of("visualization")['activate']:
                    main_controller = MainController(config)
                    view_controller = ViewController(main_controller,
                                                        config.value_of("width"),
                                                        config.value_of("height"),
                                                        config.value_of("visualization")['fps'])
                    exit(0)
                else:
                    filenames.append(p)
            else:
                filenames.extend([join(p, f) for f in listdir(p) if isfile(join(p, f))])

        print(f"Running {len(filenames)} config"
                f"{'s' if len(filenames)>1 else ''}: ",end="\t")
        print(*filenames, sep="\n\t\t\t");print("\n\n")
        if not CONFIG_FILE.RECORD_DATA:
            print("##\t"*10+"\nWARNING: data recording is disabled."
                " Set src/config(.py).RECORD_DATA to True to enable it.\n"+"##\t"*10+"\n")

    except IndexError:
        print("ERROR: no config file specified. Exiting...")
        exit(1)
        
    for i,f in enumerate(filenames):
        c = Configuration(config_file=f)
        print(f"Running config {i+1}/{len(filenames)}: {f}")
        if CONFIG_FILE.CONFIG_LOG: log_config(c,f)
        # run_processes(c)# uncomment for better config debugging  
        try:# comment here if uncommenting above
            run_processes(c)
            if exists(join(CONFIG_FILE.CONFIG_ERRORS_DIR,f.split('/')[-1])):
                system(f"rm {join(CONFIG_FILE.CONFIG_ERRORS_DIR,f.split('/')[-1])}")
                print("successfully removed file from config_errors folder")
        #TODO https://www.google.com/search?channel=fs&q=python+exception+handling+log+full+traceback
        #import logging
        except Exception as e:
        #TODO cannot catch JSONDecodeError
            with open(CONFIG_FILE.ERRORS_LOG_FILE, "a+") as fe:
                fe.write(f"{datetime.datetime.now()}, file {f} : \n"+str(e)+"\n\n")
            print(f"ERROR: {e}")
            Path(CONFIG_FILE.CONFIG_ERRORS_DIR).mkdir(parents=True, exist_ok=True)
            system(f"cp {f} {CONFIG_FILE.CONFIG_ERRORS_DIR}{f.split('/')[-1]}")
            continue

        
def run_processes(config: Configuration):
    nb_runs = config.value_of("number_runs")
    simulation_seed = config.value_of("simulation_seed")
    print(f"### {datetime.datetime.now()} # running {nb_runs} runs with {'programmed'if simulation_seed!='' and simulation_seed!='random' else 'random'} simulation seed ")
    start = time.time()
    with Pool() as pool:
        controllers = pool.starmap(run, [(config, i) for i in range(nb_runs)])
        if CONFIG_FILE.RECORD_DATA: 
            record_data(config, controllers)
            if CONFIG_FILE.CONFIG_LOG: log_config(config,generate_filename(config),output_log=True)
    print(f'###### {datetime.datetime.now()}\tFinished {nb_runs} runs in {time.time()-start: .02f} seconds.\n')


def run(config:Configuration, i):
    print(f"launched process {i+1}",end="")
    simulation_seed = config.value_of("simulation_seed")
    if simulation_seed!='' and simulation_seed!='random':
        config.set("simulation_seed", simulation_seed+i)
        print(f", setting run seed to {simulation_seed+i}")
    else: print("")
    controller = MainController(config)
    controller.start_simulation()
    return controller


def record_data(config:Configuration, controllers):
    #TODO check if passed folder arg in terminal, otherwise use this
    output_directory = config.value_of("data_collection")["output_directory"]
    filename=generate_filename(config)
    for metric in config.value_of("data_collection")["metrics"]:
    #TODO reintroduce append option, increment SEED by data already present
        if metric=="rewards":
            rewards_df = pd.DataFrame([controller.get_rewards() for controller in controllers])
            Path(join(output_directory, "rewards")).mkdir(parents=True, exist_ok=True)
            current_filename=check_filename_existence(output_directory,metric,filename)
            rewards_df.to_csv(join(output_directory, "rewards", current_filename), index=False, header=False)
        elif metric=="items_collected":
            items_collected_df = pd.DataFrame([controller.get_items_collected() for controller in controllers])
            Path(join(output_directory, "items_collected")).mkdir(parents=True, exist_ok=True)
            current_filename=check_filename_existence(output_directory,metric,filename)
            items_collected_df.to_csv(join(output_directory, "items_collected", current_filename), index=False, header=False)
        elif metric=="drifts":
            drifts_df = pd.DataFrame([controller.get_drifts() for controller in controllers])
            Path(join(output_directory, "drifts")).mkdir(parents=True, exist_ok=True)
            current_filename=check_filename_existence(output_directory,metric,filename)
            drifts_df.to_csv(join(output_directory, "drifts", current_filename), index=False, header=False)
        elif metric=="rewards_evolution":
            dataframes = []
            for i, controller in enumerate(controllers):
                df = pd.DataFrame(controller.get_rewards_evolution_list(), columns=["tick", "rewards_list"])
                df["simulation_id"] = i
                df = df.set_index("simulation_id")
                dataframes.append(df)
            Path(join(output_directory, "rewards_evolution")).mkdir(parents=True, exist_ok=True)
            current_filename=check_filename_existence(output_directory,metric,filename)
            pd.concat(dataframes).to_csv(join(output_directory, "rewards_evolution", current_filename))
        elif metric=="items_evolution":
            dataframes = []
            for i, controller in enumerate(controllers):
                df = pd.DataFrame(controller.get_items_evolution_list(), columns=["tick", "items_list"])
                df["simulation_id"] = i
                df = df.set_index("simulation_id")
                dataframes.append(df)
            Path(join(output_directory, "items_evolution")).mkdir(parents=True, exist_ok=True)
            current_filename=check_filename_existence(output_directory,metric,filename)
            pd.concat(dataframes).to_csv(join(output_directory, "items_evolution", current_filename))
        elif metric=="transactions":
            Path(join(output_directory, "transactions")).mkdir(parents=True, exist_ok=True)
            attempted_df = pd.DataFrame([controller.get_attempted_transactions_list() for controller in controllers])
            validated_df = pd.DataFrame([controller.get_validated_transactions_list() for controller in controllers])
            completed_df = pd.DataFrame([controller.get_completed_transactions_list() for controller in controllers])
            combined_df = pd.DataFrame([controller.get_combined_transactions_list() for controller in controllers])
            # current_filename=check_filename_existence(output_directory,metric,filename)
            current_filename=filename
            attempted_df.to_csv(join(output_directory, "transactions", current_filename+"_attempted"), index=False, header=False)
            validated_df.to_csv(join(output_directory, "transactions", current_filename+"_validated"), index=False, header=False)
            completed_df.to_csv(join(output_directory, "transactions", current_filename+"_completed"), index=False, header=False)
            combined_df.to_csv(join(output_directory, "transactions", current_filename+"_combined"), index=False, header=False)
        else:
            print(f"[WARNING] Could not record metric: '{metric}'. Metric name is not valid.")

    if config.value_of("data_collection")["transactions_log"]:
        transaction_logs=[]
        for i, controller in enumerate(controllers):
            df = pd.DataFrame(controller.get_transaction_log(), columns=["tick", "buyer", "seller"])
            df["simulation_id"] = i
            df = df.set_index("simulation_id")
            transaction_logs.append(df)
        Path(join(output_directory, "transactions")).mkdir(parents=True, exist_ok=True)
        current_filename=check_filename_existence(output_directory,metric,filename)
        pd.concat(transaction_logs).to_csv(join(output_directory, "transactions", current_filename))
            

def log_config(c,f,output_log=False):
    """
    log file of config runs in the selected output folder
    """
    output_directory = c.value_of("data_collection")["output_directory"]
    if not output_log:
        log_message=f"{datetime.datetime.now()}: {f}"
    else:
        log_message=f"OUTPUT FILENAME: {f}"
    if not exists(output_directory):
        Path(output_directory).mkdir(parents=True, exist_ok=True)
    with open(f"{output_directory}config_log.txt", "a+") as f:
        f.write(log_message+"\n")


if __name__ == '__main__':
    main()