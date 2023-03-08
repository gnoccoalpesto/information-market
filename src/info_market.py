import time
import pandas as pd
from multiprocessing import Pool
from pathlib import Path
from os.path import join, exists, isfile
from os import listdir
from sys import argv
import argparse

from controllers.main_controller import MainController, Configuration


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
    #TODO INCREMENTAL NAME GENERATION: if "+" in param name->add before
    #BUG wrong name generation, with passed name
    # if filename is None or filename == "":# or "+" in filename:
    #     # if "+" in filename:
    #     #     prefix=REMOVE + FROM NAME
    #     n_naive=config.value_of("behaviors")[0]['population_size']
    #     n_sceptical=config.value_of("behaviors")[1]['population_size']
    #     n_honest=n_naive+n_sceptical
    #     n_saboteur=config.value_of("behaviors")[2]['population_size']
    #     n_scaboteur=config.value_of("behaviors")[3]['population_size']
    #     n_dishonest=n_saboteur+n_scaboteur
    #     #arbitrary threshold for the naives
    #     th_honest= 3000 if n_sceptical==0 and n_honest>0 \
    #         else config.value_of("behaviors")[1]['parameters']['threshold']
    #     text_th_honest=str(th_honest).replace(".","").replace(",","")#eg 0.5 -> 05
    #     lie_angle = config.value_of("behaviors")[3]['parameters']['rotation_angle'] if n_scaboteur >0 \
    #         else config.value_of("behaviors")[2]['parameters']['rotation_angle']
    #     penalization="no" if config.value_of("payment_system")["class"]=="DelayedPaymentPaymentSystem" else ""
    #     seed=config.value_of("simulation_seed")
    #     text_seed=f"{seed if seed!='' else 'random'}"
    #     #TODO rework name convention to include more characteristics
    #     filename = \
    #         f"{n_honest}sceptical_{text_th_honest}th_"+\
    #         f"{n_dishonest}scaboteur_{lie_angle}rotation_"+\
    #         f"{penalization}penalisation_"+\
    #         f"{text_seed}Seed.csv"
    return filename

####################################################################################

def main():
    try:
        configs=[]
        filenames=[]
        for p in argv[1:]:
            if isfile(p):
                config = Configuration(config_file=p)
                configs.append(config)
                filenames.append(p)
            else:
                filenames.extend([join(p, f) for f in listdir(p) if isfile(join(p, f))])
                for f in filenames:
                    config = Configuration(config_file=f)
                    configs.append(config)
        print(f"Running {len(filenames)} config"
                f"{'s' if len(filenames)>1 else ''}: ",end="\t")
        print(*filenames, sep="\n\t\t\t")
        for c in configs:
            run_processes(c)
    except IndexError:
        print("ERROR: no config file specified, running default config.")
        exit(1)
    exit(0)

        
def run_processes(config: Configuration):
    nb_runs = config.value_of("number_runs")
    simulation_seed = config.value_of("simulation_seed")
    print(f"running {nb_runs} runs with starting simulation seed {simulation_seed if simulation_seed!='' else 'random'}")
    #TODO efficient way to create filename, check if file exists in the folders of interest, and pass
    #     the incrementing seed to the main controller
    #ISSUES: 1) what if result ofr some metric exists, but not for others?
    #        2) is it efficient to split existence/creation+to_csv, with double check? (it's not)
    start = time.time()
    with Pool() as pool:
        controllers = pool.starmap(run, [(config, i) for i in range(nb_runs)])
        record_data(config, controllers)
    print(f'######\tFinished {nb_runs} runs in {time.time()-start: .02f} seconds.\n')


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
    #TODO reintroduce append option, butwhat about seed?
    #TODO more parametric, use dict of functions and pass args
        # match metric:
        # case "rewards":
        if metric=="rewards":
            rewards_df = pd.DataFrame([controller.get_rewards() for controller in controllers])
            Path(join(output_directory, "rewards")).mkdir(parents=True, exist_ok=True)
            #TODO fix append then use this
            # if seed!='' and seed!='random':
            current_filename=check_filename_existence(output_directory,metric,filename)
            rewards_df.to_csv(join(output_directory, "rewards", current_filename), index=False, header=False)
        # case "items_collected":
        elif metric=="items_collected":
            items_collected_df = pd.DataFrame([controller.get_items_collected() for controller in controllers])
            Path(join(output_directory, "items_collected")).mkdir(parents=True, exist_ok=True)
            current_filename=check_filename_existence(output_directory,metric,filename)
            items_collected_df.to_csv(join(output_directory, "items_collected", current_filename), index=False, header=False)
        # case "drifts":
        elif metric=="drifts":
            drifts_df = pd.DataFrame([controller.get_drifts() for controller in controllers])
            Path(join(output_directory, "drifts")).mkdir(parents=True, exist_ok=True)
            current_filename=check_filename_existence(output_directory,metric,filename)
            drifts_df.to_csv(join(output_directory, "drifts", current_filename), index=False, header=False)
        # case "rewards_evolution":
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
        # case "items_evolution":
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
        # case _:
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
            

if __name__ == '__main__':
    main()