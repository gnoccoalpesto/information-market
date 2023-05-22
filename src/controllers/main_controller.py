import json
import numpy as np

from helpers import random_walk
from model.environment import Environment
import config as CONFIG_FILE


class Configuration:
    def __init__(self, config_file):
        self._parameters = self.read_config(config_file)

    def __contains__(self, item):
        return item in self._parameters

    @staticmethod
    def read_config(config_file):
        with open(config_file, "r") as file:
            return json.load(file)

    def save(self, save_path):
        json_object = json.dumps(self._parameters, indent=2)
        with open(save_path, 'w') as file:
            file.write(json_object)

    def value_of(self, parameter):
        return self._parameters[parameter]

    def set(self, parameter, value):
        self._parameters[parameter] = value


class MainController:

    def __init__(self, config: Configuration):
        self.config = config
        random_walk.set_parameters(**self.config.value_of('random_walk'),
                                   max_levi_steps=self.config.value_of("simulation_steps")+1
                                   )
        self.environment = Environment(width=self.config.value_of("width"),
                                       height=self.config.value_of("height"),
                                       agent_params=self.config.value_of("agent"),
                                       behavior_params=self.config.value_of("behaviors"),
                                       combine_strategy_params=self.config.value_of("combine_strategy"),
                                       food=self.config.value_of("food"),
                                       nest=self.config.value_of("nest"),
                                       payment_system_params=config.value_of("payment_system"),
                                       market_params=config.value_of("market"),
                                       simulation_seed=config.value_of("simulation_seed"),
                                       )
        self.tick = 0


    def step(self):
        if self.tick % self.config.value_of("data_collection")['precise_recording_interval'] == 0:
            if "rewards_evolution" in self.config.value_of("data_collection")["metrics"]:
                self.rewards_evolution_list.append([self.tick, self.get_rewards()])
            if "items_evolution" in self.config.value_of("data_collection")["metrics"]:
                self.items_evolution_list.append([self.tick, self.get_items_collected()])
            if hasattr(self.environment.payment_database.database[0]["payment_system"], "pot_amount"):
                self.stake_pot_evolution_list.append([self.tick, self.get_stake_pots()])
                self.wealth_evolution_list.append([self.tick,[r+p for r,p in zip(self.rewards_evolution_list[-1][1],self.stake_pot_evolution_list[-1][1])]])
            # if CONFIG_FILE.LOG_EXCEPTIONS:
            #     self.IFE_evolution_list.append([self.tick,self.get_IFE()])
        self.tick += 1
        self.environment.step()
            

    def start_simulation(self):
        self.init_statistics()
        for _ in range(self.config.value_of("simulation_steps")):
            self.step()
        #[ ] NEWCOMERS PHASE
        if CONFIG_FILE.NEWCOMER_PHASE:
            # self.init_statistics(newcomers_phase=True)
            self.environment.create_newcomers(CONFIG_FILE.NEWCOMER_TYPE, CONFIG_FILE.NEWCOMER_AMOUNT)
            for _ in range(CONFIG_FILE.NEWCOMER_PHASE_DURATION):
                self.step()


    def init_statistics(self):#,newcomers_phase=False):
        #TODO newcomers phase re-init
        # if newcomers_phase:
        #     CONFIG_FILE.IFE_COUNT+=[0]*CONFIG_FILE.NEWCOMER_AMOUNT
        #     CONFIG_FILE.NIS_COUNT+=[0]*CONFIG_FILE.NEWCOMER_AMOUNT
        #     return
        self.rewards_evolution_list = []
        self.items_evolution_list = []
        self.stake_pot_evolution_list=[]
        self.wealth_evolution_list=[]
        # if CONFIG_FILE.LOG_EXCEPTIONS:
        #     self.IFE_evolution_list=[]
        #   self.NIS_COUNT=[0]*self.environment.ROBOTS_AMOUNT


    def get_sorted_reward_stats(self):
        sorted_bots = sorted([bot for bot in self.environment.population], key=lambda bot: abs(bot.noise_mu))
        res = ""
        for bot in sorted_bots:
            res += str(bot.reward()) + ","
        res = res[:-1]  # remove last comma
        res += "\n"
        return res


    def get_reward_stats(self):
        res = ""
        for bot in self.environment.population:
            res += str(bot.reward()) + ","
        res = res[:-1]
        res += "\n"
        return res


    def get_rewards(self):
        return [bot.reward() for bot in self.environment.population]


    def get_items_collected(self):
        return [bot.items_collected for bot in self.environment.population]


    def get_drifts(self):
        return [bot.noise_mu for bot in self.environment.population]


    def get_items_collected_stats(self):
        res = ""
        for bot in self.environment.population:
            res += str(bot.items_collected) + ","
        res = res[:-1]
        res += "\n"
        return res


    def get_drift_stats(self):
        res = ""
        for bot in self.environment.population:
            res += str(bot.noise_mu) + ","
        res = res[:-1]
        res += "\n"
        return res
    

    def get_stake_pots(self):
        return [self.environment.payment_database.get_stake_pot(bot.id) for bot in self.environment.population]


    # def get_IFE(self):
    #     return [bot.IFE for bot in self.environment.population]


    def get_robot_at(self, x, y):
        return self.environment.get_robot_at(x, y)


    def get_robot_by_id(self, id):
        return self.environment.get_robot_by_id(id)


    def get_rewards_evolution(self):
        return self.rewards_evolution


    def get_rewards_evolution_list(self):
        return self.rewards_evolution_list


    def get_items_evolution_list(self):
        return self.items_evolution_list
    

    def get_stake_pot_evolution_list(self):
        return self.stake_pot_evolution_list


    def get_wealth_evolution_list(self):
        return self.wealth_evolution_list

    def get_transaction_log(self):
        return self.environment.payment_database.completed_transactions_log


    def get_transactions_list(self,type:str,role="buyer"):
        '''
        :param type of transaction desidered. Accepted values are:
            "attempted"("A","a"),"validated","completed"("C","c"),"combined"
        :param role in the transaction. Accepted values are: "buyer" or "seller".
        
        :return a list of {type} transactions, where element is the amount of 
            transactions where each robot took part as {role}
        '''
        transaction_matrix=np.array([self.environment.payment_database.get_transactions(type,bot.id) \
                                        for bot in self.environment.population])
        if role=="buyer":
            return transaction_matrix.sum(axis=1)
        return transaction_matrix.sum(axis=0)
