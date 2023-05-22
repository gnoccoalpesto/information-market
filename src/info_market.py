import time
import re
import datetime
import pandas as pd
from multiprocessing import Pool
from pathlib import Path
from os.path import join, exists, isfile, isdir
from os import listdir, system
from sys import argv
import logging
# import argparse
# from json.decoder import JSONDecodeError

import config as CONFIG_FILE
from controllers.main_controller import MainController, Configuration
from model.behavior import BAD_PARAM_COMBINATIONS_DICT, BEHAVIORS_NAME_DICT, BEHAVIOR_PARAMS_DICT, \
    PARAMS_NAME_DICT, NOISE_PARAMS_DICT, BEST_PARAM_COMBINATIONS_DICT,COMBINE_STRATEGY_NAME_DICT, \
    SUB_FOLDERS_DICT


############################################################################################################
############################################################################################################
####################################### UTILITIES ##########################################################
#TODO def parse_args():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-a', '--all',action='store_true',required=False,
#                     help='use all files from a single folder')
#     args=parser.parse_args()
#     if args.all:
#         select_all=True
#     return select_all


#TODO return NRS or RS instead of True or False; change everything accordingly
def params_from_filename(filename:str, compact_format:bool=False):
    """
    :param compact_format: if True, returns the initials, and only the values of the parameters instead of the label text
    filename format:
    nhonestHONESTBEHAVIOUR_PAYMENTSYSTEM_lieangleLIA_behaviorparams_noiseparams

    HONESTBEHAVIOUR =   "n": "NaiveBeahvior",
                        "Nn": "NewNaiveBehavior",
                        "s": "ScepticalBehavior",
                        "Ns": "NewScepticalBehavior",
                        "r": "ReputationRankingBehavior",
                        "v": "VariableScepticalBehavior",
                        "Nv": "NewVariableScepticalBehavior",
                        "t": "WealthThresholdBehavior",
                        "w": "WealthWeightedBehavior",

    COMBINESTRATEGY =   
                        "waa" : "WeightedAverageAgeStrategy"
                        "wara" : "WeightedAverageReputationAgeStrategy"
                        "rwar" : "RunningWeightedAverageReputationStrategy"
                        "nrwar" : "NewRunningWeightedAverageReputationStrategy"
                        "fwar" : "FullWeightedAverageReputationStrategy"
                        "nfwar" : "NewFullWeightedAverageReputationStrategy"

    PAYMENTSYSTEM =     "NP": "No Penalization",
                        "P": "Penalization",

    REPUTATION STAKE =  "RS": "ReputationStake",
                        "NRS": "NoReputationStake",

                        
    lieangle =          [0, 90]

    behaviorparams =    "n","Nn","w":   {}, NOTE: CS: combine strategy for all just for simplicity
                        "s","Ns":       {"ST": "scepticism threshold"},
                        "r":            {"RT": "ranking threshold"},
                        "v","Nv":       {"CM": "comparison method",
                                        "SC": "scaling",
                                        "ST": "scepticism threshold",
                                        "WM": "weight method"},
                        "t":            {"CM": "comparison method",
                                        "SC": "scaling"}

                        "h":            {"VM":verification method,
                                        "TM": threshold method,
                                        "SC": scaling,
                                        "KD": differential controller coeff,
                                        "RS": reputation staking,}
                                            
    noiseparams =       "bimodal":      {"SMU": "noise sampling mean",
                                        "SSD": "noise sampling standard deviation",
                                        "NSD": "noise standard deviation"},
                        "uniform":      {"NMU": "noise mean",
                                        "NRANG": "noise range",
                                        "SAB": "saboteur performance" ={"avg": "average",
                                                                        "perf": "perfect"}}

    :return if compact_format: n_honest, honest_behavior, combine_strategy, payment, lie_angle, behaviour_params, noise_params
            else: n_honest, honest_behavior, combine_strategy, payment, lie_angle, behaviour_params, noise_params, message
    """
    if "/" in filename: filename=filename.split("/")[-1]
    if filename.endswith(".json"): filename=filename.split(".json")[0]
    elif filename.endswith(".csv"): filename=filename.split(".csv")[0]
    params=filename.split("_")

    #TODO look for specific keywords instead of using position
    n_honest=re.search('[0-9]+', params[0]).group()
    lie_angle=re.search('[0-9]+', params[4]).group()
    reputation_stake=True if params[3].split("RS")[0]=="" else False
    behaviour_params_list=params[5:-3]
    noise_params_list=params[-3:]

    if compact_format:
        honest_behavior="".join(re.findall('[a-zA-Z]+', params[0]))
        combine_strategy="".join(re.findall('[a-z]+', params[1]))
        payment=params[2]
        behaviour_params=[]
        for p in behaviour_params_list:
            behaviour_params.append("".join(re.findall('[0-9a-z]+', p)))
        noise_params=[]
        for p in noise_params_list:
            noise_params.append("".join(re.findall('[0-9a-z]+', p)))
        return n_honest, honest_behavior,combine_strategy, payment, reputation_stake, lie_angle, behaviour_params, noise_params

    honest_behavior=BEHAVIORS_NAME_DICT["".join(re.findall('[a-zA-Z]+', params[0]))]
    combine_strategy=COMBINE_STRATEGY_NAME_DICT["".join(re.findall('[a-z]+', params[1]))]
    payment=PARAMS_NAME_DICT[params[2]]
    
    behaviour_params=""
    for p in behaviour_params_list:
        #TODO can make this more compact using the ones from compact_format
        value="".join(re.findall('[0-9a-z]+', p))
        behaviour_params+=f"{value} {PARAMS_NAME_DICT[''.join(re.findall('[A-Z]+', p))]},"
    behaviour_params=behaviour_params[:-1]
    
    noise_params=""
    for p in noise_params_list:
        value="".join(re.findall('[0-9a-z]+', p))
        noise_params+=f"{value} {PARAMS_NAME_DICT[''.join(re.findall('[A-Z]+', p))]},"
    noise_params=noise_params[:-1]
    
    message=f"{n_honest} {honest_behavior},\n {combine_strategy},\n{payment}, lie_angle: {lie_angle},\n{behaviour_params},\n{noise_params}"
    
    return n_honest, honest_behavior, combine_strategy, payment, reputation_stake, lie_angle, behaviour_params, noise_params, message
        

def filename_from_params(n_honests:int,
                        behavior_initials:str,
                        combine_strategy_initials:str,
                        payment_system:str,
                        reputation_stake:bool,
                        lie_angle:int,
                        behavior_params_values:list,
                        noise_type:str,
                        noise_params_values:list
                        ):
    if isinstance(reputation_stake, bool):
    #NOTE else it is supposed to be a string ={"RS","NRS"}
        if reputation_stake: reputation_stake="RS"
        else: reputation_stake="NRS"
    behavior_params=""
    if behavior_params_values:
        for x,y in zip(behavior_params_values,BEHAVIOR_PARAMS_DICT[behavior_initials]):
            behavior_params+=f"{x}{y}_"
    noise_params=""
    for x,y in zip(noise_params_values,NOISE_PARAMS_DICT[noise_type]):
        noise_params+=f"{x}{y}_"
    noise_params=noise_params[:-1]
    filename=f"{n_honests}{behavior_initials}_{combine_strategy_initials}CS_{payment_system}_{reputation_stake}_{lie_angle}LIA_{behavior_params}{noise_params}"
    return filename


def is_bad_param_combination(filename:str):
    _, h_behav, _, payment, reputation_stake,_, behav_params, _ = params_from_filename(filename,compact_format=True)
    if [payment,reputation_stake, behav_params] in BAD_PARAM_COMBINATIONS_DICT[h_behav]:
        return True
    return False
    

def is_best_param_combination(filename:str):
    _, h_behav, _, payment, reputation_stake,_, behav_params, _ = params_from_filename(filename,compact_format=True)
    reputation_stake="RS" if reputation_stake else "NRS"
    if [payment, reputation_stake, behav_params] in BEST_PARAM_COMBINATIONS_DICT[h_behav]:
        return True
    return False


def prune_params_combinations(filenames:list,best_mode=False):
    count=0
    try:
        #BUG works only with reversed order (LOL)
        for f in reversed(filenames):
            if (not best_mode and is_bad_param_combination(f)) or \
                    (best_mode and not is_best_param_combination(f)):
                filenames.remove(f)
                #UNUSED system(f"rm {f}")
                count+=1
        if count>0:
            prune_method="maintained only the best combinations" if best_mode else "removed the bad combinations"
            print(f"- - - - - ATTENTION: {prune_method} of payment & behavioural parameters - - - - - -")
            print(f"- - - - - number of combinations pruned: {count}\t"+"- "*25+"\n")
    except AttributeError:
        #catches if filename has not the standard format. For test purposes
        pass
    return filenames


####################################################################################
####################################################################################
class InformationMarket():
    def __init__(self) -> None:
        self.logger=logging
        self.logger.basicConfig(filename=CONFIG_FILE.ERRORS_LOG_FILE, level=logging.DEBUG)
        self.main()


    @staticmethod
    def check_filename_existence(output_directory,metric,filename:str):
        new_filename = filename.split('/')[-1]
        if exists(join(output_directory, metric, filename)):
            exist_count = len([f for f in Path(join(output_directory, metric)).iterdir() \
                if f.name.startswith(new_filename.split(".csv")[0])])
            new_filename = new_filename.replace(".csv", f"_{exist_count}.csv")
        return new_filename


    @staticmethod
    def generate_filename(config:Configuration,):
        filename = config.value_of("data_collection")["filename"]
        return filename

    @staticmethod
    #OVERLOADED WHEN GUI AVAILABLE
    def launch_view_controller(main_controller:MainController,c:Configuration):
        print('WARNING: no GUI interface available')
        return None


    def main(self):
        try:
            filenames=[]
            for p in argv[1:]:
                if isfile(p):
                    config = Configuration(config_file=p)
                    if config.value_of("visualization")['activate']:
                        main_controller = MainController(config)
                        view_controller=self.launch_view_controller(main_controller,config)
                        exit(0)
                    else:
                        filenames.append(p)
                    continue
                elif p in SUB_FOLDERS_DICT:
                    p=join(CONFIG_FILE.CONFIG_DIR,SUB_FOLDERS_DICT[p])
                if isdir(p):
                    filenames.extend([join(p, f) for f in listdir(p) if isfile(join(p, f))])
                else:
                    print(f"WARNING: {p} is not a valid config file or directory. Skipping it...\n")

            if CONFIG_FILE.PRUNE_FILENAMES:
                filenames=prune_params_combinations(filenames,best_mode=CONFIG_FILE.PRUNE_NOT_BEST)

            print(f"Running {len(filenames)} config"
                    f"{'s' if len(filenames)>1 else ''}: ",end="\n")
            print(*filenames, sep="\n");print("\n\n")
            if not CONFIG_FILE.RECORD_DATA:
                print("##\t"*10+"\nWARNING: data recording is disabled."
                    " Set src/config(.py).RECORD_DATA to True to enable it.\n"+"##\t"*10+"\n")
            
        except IndexError:
            print("ERROR: no config file specified. Exiting...")
            exit(1)
            
        for i,f in enumerate(filenames):
            c = Configuration(config_file=f)
            print(f"Running config {i+1}/{len(filenames)}: {f}")
            if CONFIG_FILE.CONFIG_RUN_LOG: self.log_config(c,f)
            try:
                self.run_processes(c)
                if exists(join(CONFIG_FILE.CONFIG_ERRORS_DIR,f.split('/')[-1])):
                    system(f"rm {join(CONFIG_FILE.CONFIG_ERRORS_DIR,f.split('/')[-1])}")
                    print(f"#-#-#- [[successfully removed {join(CONFIG_FILE.CONFIG_ERRORS_DIR,f.split('/')[-1])}]]\n")
                else: print()

            except Exception as e:
            #BUG cannot catch JSONDecodeError
                self.logger.exception(F"{datetime.datetime.now()}, file {f} : \n")
                with open(CONFIG_FILE.ERRORS_LOG_FILE, "a+") as fe:
                    fe.write("\n"+"#"*100+"\n\n")

                Path(CONFIG_FILE.CONFIG_ERRORS_DIR).mkdir(parents=True, exist_ok=True)
                system(f"cp {f} {join(CONFIG_FILE.CONFIG_ERRORS_DIR,f.split('/')[-1])}")

                print(f"LOGGED ERROR: {e}\n")
                continue
                #[ ] pass #could resolve the InsufficientFunds bug

            
    def run_processes(self,config: Configuration):
        nb_runs = config.value_of("number_runs")
        simulation_seed = config.value_of("simulation_seed")
        print(f"### {datetime.datetime.now()} # running {nb_runs} runs with {'programmed'if simulation_seed!='' and simulation_seed!='random' else 'random'} simulation seed ")
        start = time.time()
        with Pool() as pool:
            controllers = pool.starmap(self.run, [(config, i) for i in range(nb_runs)])
            
            if CONFIG_FILE.RECORD_DATA: 
                items_filename=self.record_data(config, controllers)
                if CONFIG_FILE.CONFIG_RUN_LOG:
                    #TODO use as output name in log the one with similar filenames counter 
                    # if items_filename is None:
                    self.log_config(config,self.generate_filename(config),output_log=True)
                    # else:
                    #     self.log_config(None,items_filename,output_log=True)
        print(f'###### {datetime.datetime.now()}\tFinished {nb_runs} runs in {time.time()-start: .02f} seconds')


    @staticmethod
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


    def record_data(self,config:Configuration, controllers):
        output_directory = config.value_of("data_collection")["output_directory"]
        filename=self.generate_filename(config)
        CAN_RETURN=False
        for metric in config.value_of("data_collection")["metrics"]:
        #TODO reintroduce append option, increment SEED by data already present
            if metric=="rewards":
                #TODO substitute "metric" w metric
                rewards_df = pd.DataFrame([controller.get_rewards() for controller in controllers])
                Path(join(output_directory, "rewards")).mkdir(parents=True, exist_ok=True)
                current_filename=self.check_filename_existence(output_directory,metric,filename)
                items_filename=current_filename
                CAN_RETURN=True
                rewards_df.to_csv(join(output_directory, "rewards", current_filename), index=False, header=False)
            elif metric=="items_collected":
                items_collected_df = pd.DataFrame([controller.get_items_collected() for controller in controllers])
                Path(join(output_directory, "items_collected")).mkdir(parents=True, exist_ok=True)
                current_filename=self.check_filename_existence(output_directory,metric,filename)
                items_collected_df.to_csv(join(output_directory, "items_collected", current_filename), index=False, header=False)
            elif metric=="drifts":
                drifts_df = pd.DataFrame([controller.get_drifts() for controller in controllers])
                Path(join(output_directory, "drifts")).mkdir(parents=True, exist_ok=True)
                current_filename=self.check_filename_existence(output_directory,metric,filename)
                drifts_df.to_csv(join(output_directory, "drifts", current_filename), index=False, header=False)
            elif metric=="rewards_evolution":
                dataframes = []
                for i, controller in enumerate(controllers):
                    df = pd.DataFrame(controller.get_rewards_evolution_list(), columns=["tick", "rewards_list"])
                    df["simulation_id"] = i
                    df = df.set_index("simulation_id")
                    dataframes.append(df)
                Path(join(output_directory, "rewards_evolution")).mkdir(parents=True, exist_ok=True)
                current_filename=self.check_filename_existence(output_directory,metric,filename)
                pd.concat(dataframes).to_csv(join(output_directory, "rewards_evolution", current_filename))
            elif metric=="items_evolution":
                dataframes = []
                for i, controller in enumerate(controllers):
                    df = pd.DataFrame(controller.get_items_evolution_list(), columns=["tick", "items_list"])
                    df["simulation_id"] = i
                    df = df.set_index("simulation_id")
                    dataframes.append(df)
                Path(join(output_directory, "items_evolution")).mkdir(parents=True, exist_ok=True)
                current_filename=self.check_filename_existence(output_directory,metric,filename)
                pd.concat(dataframes).to_csv(join(output_directory, "items_evolution", current_filename))
            elif "transactions" in metric:
                Path(join(output_directory, "transactions")).mkdir(parents=True, exist_ok=True)
                transaction_types=["attempted","validated","completed","combined"]
                roles_transaction=["buyer","seller"]
                for transaction_type in transaction_types:
                    for transaction_role in roles_transaction:
                        transactions_df = pd.DataFrame([controller.get_transactions_list(transaction_type,transaction_role) \
                                                            for controller in controllers])
                        Path(join(output_directory, "transactions")).mkdir(parents=True, exist_ok=True)
                
                        complete_filename=join(filename.split(".csv")[0]+f"_{transaction_type}_{transaction_role}.csv")
                        current_filename=self.check_filename_existence(output_directory,metric,complete_filename)
                        transactions_df.to_csv(join(output_directory, "transactions", current_filename), index=False, header=False)
            else:
                print(f"[WARNING] Could not record metric: '{metric}'. Metric name is not valid.")
        
        if config.value_of("data_collection")["transactions_log"]:
        #NOTE --- ATTENTION: this files can easily reach 200MB each
            transaction_logs=[]
            for i, controller in enumerate(controllers):
                df = pd.DataFrame(controller.get_transaction_log(), columns=["tick", "buyer", "seller"])
                df["simulation_id"] = i
                df = df.set_index("simulation_id")
                transaction_logs.append(df)
            Path(join(output_directory, "transactions")).mkdir(parents=True, exist_ok=True)
            current_filename=self.check_filename_existence(output_directory,metric,filename)
            pd.concat(transaction_logs).to_csv(join(output_directory, "transactions", current_filename))
            
        if hasattr(controllers[0].environment.payment_database.database[0]["payment_system"], "pot_amount"):
            dataframes = []
            for i, controller in enumerate(controllers):
                df = pd.DataFrame(controller.get_stake_pot_evolution_list(), columns=["tick", "pot_list"])
                df["simulation_id"] = i
                df = df.set_index("simulation_id")
                dataframes.append(df)
            Path(join(output_directory, "pots_evolution")).mkdir(parents=True, exist_ok=True)
            current_filename=self.check_filename_existence(output_directory,metric,filename)
            pd.concat(dataframes).to_csv(join(output_directory, "pots_evolution", current_filename))
            dataframes = []
            for i, controller in enumerate(controllers):
                df = pd.DataFrame(controller.get_wealth_evolution_list(), columns=["tick", "wealth_list"])
                df["simulation_id"] = i
                df = df.set_index("simulation_id")
                dataframes.append(df)
            Path(join(output_directory, "wealth_evolution")).mkdir(parents=True, exist_ok=True)
            current_filename=self.check_filename_existence(output_directory,metric,filename)
            pd.concat(dataframes).to_csv(join(output_directory, "wealth_evolution", current_filename))

        # if CONFIG_FILE.LOG_EXCEPTIONS:
        #     Path(join(output_directory, "exceptions")).mkdir(parents=True, exist_ok=True)
        #     current_filename=self.check_filename_existence(output_directory,metric,filename)

        return items_filename if CAN_RETURN else None


    @staticmethod
    def log_config(c,f,output_log=False):
        """
        log file of config runs in the selected output folder
        """
        output_directory = c.value_of("data_collection")["output_directory"] if c is not None \
                        else "/".join(f.split("/")[:-1])
        if not output_log:
            log_message=f"{datetime.datetime.now()}: {f}"
        else:
            log_message=f"OUTPUT FILENAME: {f}"
        if not exists(output_directory):
            Path(output_directory).mkdir(parents=True, exist_ok=True)
        with open(join(output_directory,"config_log.txt"), "a+") as f:
            f.write(log_message+"\n")


##########################################################################################
##########################################################################################
##########################################################################################
if __name__ == '__main__':
    #overload when visual capabilities are available
    if exists(join(CONFIG_FILE.PROJECT_DIR,"src","gui.py")):
        #NOTE import error suppressed since gui.py is not available in headless mode
        from gui import InformationMarket# type: ignore # pylint: disable=import-error

    infomarket=InformationMarket()

'''
TODO run visual simulations consequently
def main2():
    try:
        filenames=[]
        for p in argv[1:]:
            if p in SUB_FOLDERS_DICT:
                p=join(CONFIG_FILE.CONFIG_DIR,SUB_FOLDERS_DICT[p])

            if isdir(p):

            elif isfile(p):

            else:
                print(f"WARNING")
                

    SHOWED_WARNING_RECORD_DATA=False
    for i,f in enumerate(filenames):
        try:
            if c.value_of("visualization")["activate"]:
                main_controller = MainController(c)
                view_controller = launch_view_controller(main_controller, c)
            else:
                if not CONFIG_FILE.RECORD_DATA and not SHOWED_WARNING_RECORD_DATA:
                    print("##\t"*10+"\nWARNING: data recording is disabled."
                        " Set src/config(.py).RECORD_DATA to True to enable it.\n"+"##\t"*10+"\n")

                run_processes(c)

        except Exception as e: ...

'''