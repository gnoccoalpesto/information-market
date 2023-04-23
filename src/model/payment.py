from abc import ABC, abstractmethod
from collections import Counter
import numpy as np
import pandas as pd

import config as CONFIG_FILE
from helpers.utils import InsufficientFundsException
from model.navigation import Location

#torns off warning when working with on slices of DataFrames
pd.options.mode.chained_assignment = None


class Transaction:
    def __init__(self, buyer_id, seller_id, location, info_relative_angle, timestep):
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.location = location
        self.relative_angle = info_relative_angle
        self.timestep = timestep


class PaymentAPI:
    def __init__(self, payment_db):
        self.apply_gains = payment_db.apply_gains
        self.apply_cost = payment_db.apply_cost
        self.transfer = payment_db.transfer
        self.update_history = payment_db.update_history


class PaymentDB:
    """
    data stored on the blockchain:
    - reward (float): the amount of reward the robot has at the moment;
    - payment_system (PaymentSystem): the payment system used by the robot;
    - age (int): the age of the robot, exoressed in number of ticks;
    - n_attempted_transactions (int): the number of transactions the robot was involved in;
    - n_validated_transactions (int): the number of transactions that pass the information validity test;
    - n_completed_transactions (int): the number of transactions where the robot bought information;
    - n_combined_transactions (int): the number of transactions where the robot used the data;
    - reward_trend (?): the trend of the reward of the robot. Could be expressed
        qith derivative, difference or sign of the difference;
    - n_transactions_trend (?): the trend of the number of transactions of the robot.
    """
    def __init__(self, population_ids, payment_system_params):
        #TODO hardcoded
        self.history_span=10
        self.database = {}
        for robot_id in population_ids:
            self.database[robot_id] = {"reward": payment_system_params["initial_reward"],
                                       "payment_system": eval(payment_system_params['class'])(
                                                                **payment_system_params['parameters']),
                                        "wallet_age": 0,
                                        #TODO make n_transactions a DICT
                                        "n_attempted_transactions": [0]*len(population_ids),
                                        #UNUSED "n_validated_transactions": 0,
                                        "n_completed_transactions": [0]*len(population_ids),
                                        "n_combined_transactions" : [0]*len(population_ids),
                                        #NOTE history is loaded bottom->top
                                        "history": [None]*self.history_span,
                                        # "reward_trend": 0,
                                        # "n_transactions_trend": 0,
                                        # LOCATIONS COULD PUT TOO MUCH STRESS <- CONTINUOUS UPDATE
                                        #->TODO COULD USE A DATE INSTEAD
                                        # "locations_acquisition": {Location.FOOD: 0,
                                        #                  Location.NEST: 0
                                        #                 }
                                    }
        self.completed_transactions_log=[]


    def update_history(self,robot_id,redistribution):
        #[ ]
        self.database[robot_id]["history"].pop(0)
        self.database[robot_id]["history"].append(redistribution)


    def get_history(self,robot_id):
        #[ ]
        return self.database[robot_id]["history"]

    def increment_wallet_age(self, robot_id):
        self.database[robot_id]["wallet_age"] += 1


    def pay_reward(self, robot_id, reward=1):
        self.database[robot_id]["reward"] += reward


    def transfer(self, from_id, to_id, amount):
        if amount < 0:
            raise ValueError("Amount must be positive")
        self.apply_cost(from_id, amount)
        self.apply_gains(to_id, amount)


    def record_transaction(self,type:str,buyer_id:int,seller_id:int,transaction:Transaction=None):
        #TODO make this more similar to self.get_transactions()
        if type=="completed" or type=="C" or type=="c":
            self.database[transaction.buyer_id]["n_completed_transactions"][seller_id] += 1
            self.database[transaction.buyer_id]["payment_system"].new_transaction(transaction, PaymentAPI(self))
            if CONFIG_FILE.LOG_COMPLETED_TRANSATIONS: self.log_completed_transaction(transaction)
        elif type=="attempted" or type=="A" or type=="a":
            self.database[buyer_id]["n_attempted_transactions"][seller_id] += 1
        # elif type=="validated" or type=="V" or type=="v":
        #     self.database[buyer_id]["n_validated_transactions"][seller_id] += 1
        elif type=="combined" or type=="X" or type=="x":
            self.database[buyer_id]["n_combined_transactions"][seller_id] += 1
        else:
            raise ValueError("Transaction type not recognized")


    def pay_creditors(self, debitor_id, total_reward=1):
        self.database[debitor_id]["payment_system"].new_reward(total_reward, PaymentAPI(self),
                                                               debitor_id)


    def get_total_reward(self):
        #TODO rework
        return sum([self.database[robot_id]["reward"] for robot_id in self.database])
        

    def get_reward(self, robot_id):
        #TODO remove
        return self.database[robot_id]["reward"]


    def get_reputation(self, robot_id,method="reward",verification_method="last"):
        #TODO unify below
        if method=="reward" or method=="r" or method=="R" or method=="w":
            return self.get_reward(robot_id)
        #[ ]
        elif method=="history" or method=="h" or method=="H":
            valid_history=[h for h in self.database[robot_id]["history"] if h]

            # try:
            if len(valid_history)>1 and verification_method=="last":
            # return valid_history[-1] >= 0
                result=valid_history[-1]
            elif len(valid_history)>2:
                if verification_method=="last2":
                    # return valid_history[-1] >= valid_history[-2]
                    result=max(valid_history[-1],valid_history[-2])
                else:
                    reputation=0
                    previous_h=None
                    for i,h in enumerate(valid_history):
                        if previous_h is None:
                            previous_h=h
                        else:
                            if verification_method=="discrete":
                                increment=np.sign(h-previous_h)*1
                            elif verification_method=="difference":
                                increment=np.sign(h-previous_h)*(h-previous_h)
                            elif verification_method=="aged":
                                increment=np.sign(h-previous_h)*(h-previous_h)*(i+1)
                            elif verification_method=="derivative":
                                increment=np.sign(h-previous_h)*(h-previous_h)/(len(valid_history)-i)
                            elif verification_method=="derivative2":
                                increment=np.sign(h-previous_h)*(h-previous_h)/(len(valid_history)-i)**2

                            reputation+=increment
                            previous_h=h
                    result=reputation
            else:
                result=0
            return result
            # except UnboundLocalError:
            #     return 0


            # for i,h in enumerate(valid_history):
            #     if previous_h is None:
            #         previous_h=h
            #     else:
            #         if verification_method=="discrete":
            #             increment=np.sign(h-previous_h)*1
            #         elif verification_method=="difference":
            #             increment=np.sign(h-previous_h)*(h-previous_h)
            #         elif verification_method=="aged":
            #             increment=np.sign(h-previous_h)*(h-previous_h)*(i+1)
            #         elif verification_method=="derivative":
            #             increment=np.sign(h-previous_h)*(h-previous_h)/(len(valid_history)-i)
            #         elif verification_method=="derivative2":
            #             increment=np.sign(h-previous_h)*(h-previous_h)/(len(valid_history)-i)**2

            #         reputation+=increment
            #         previous_h=h
            # print("reputation",reputation)
            # return reputation


    def get_highest_reward(self):
        #TODO remove
        return np.max([self.database[robot_id]["reward"] for robot_id in self.database])


    def get_lowest_reward(self):
        return np.min([self.database[robot_id]["reward"] for robot_id in self.database])

    
    def get_mean_reward(self):
        return np.average([self.database[robot_id]["reward"] for robot_id in self.database])


    def get_highest_reputation(self,method="reward"):
        #TODO unify
        if method=="reward" or method=="r" or method=="R" or method=="w":
            return self.get_highest_reward()
        #[ ]
        elif method=="history" or method=="h" or method=="H":
            return np.max([self.get_reputation(robot_id,method="history") for robot_id in self.database])


    def get_lowest_reputation(self,method="reward"):
        if method=="reward" or method=="r" or method=="R" or method=="w":
            return self.get_lowest_reward()
        #[ ]
        elif method=="history" or method=="h" or method=="H":
            return np.min([self.get_reputation(robot_id,method="history") for robot_id in self.database])
    

    def get_mean_reputation(self,method="reward",verification_method="last"):
        if method=="reward" or method=="r" or method=="R" or method=="w":
            return self.get_mean_reward()
        #[ ]
        elif method=="history" or method=="h" or method=="H":
            method="history"
            return np.mean([self.get_reputation(robot_id,method,verification_method) for robot_id in self.database])


    def get_sorted_database(self,method="reward"):
        """
        returns blockchain (dict), sorted by highest reward first
        """
        if method=="reward" or method=="r" or method=="R" or method=="w":
            sorted_database = dict(sorted(self.database.items(), 
                                key=lambda x: x[1]["reward"], reverse=True))
        return sorted_database
        
    
    def get_reward_ranking(self,robot_id):
        sorted_database = self.get_sorted_database()
        return list(sorted_database.keys()).index(robot_id)

    
    def get_reputation_ranking(self,robot_id,method="reward"):
        if method=="reward" or method=="r" or method=="R" or method=="w":
            return self.get_reward_ranking(robot_id)
        #[ ]
        elif method=="history" or method=="h" or method=="H":
            reputations=[self.get_reputation(robot_id,method="history") for robot_id in self.database]
            return list



    def get_number_of_wallets(self):
        return len(self.database)


    def apply_cost(self, robot_id, cost):
        '''cost of motion, stopping,recharge, etc.'''
        if cost < 0:
            raise ValueError("Cost must be positive")
        if self.database[robot_id]["reward"] < cost:
            raise InsufficientFundsException
        else:
            self.database[robot_id]["reward"] -= cost


    def apply_gains(self, robot_id, gains):
        if gains < 0:
            raise ValueError("Gains must be positive")
        self.database[robot_id]["reward"] += gains


    def log_completed_transaction(self,transaction:Transaction):
        self.completed_transactions_log.append([transaction.timestep,transaction.buyer_id,transaction.seller_id])


    def get_transactions(self,type:str,robot_id:int):
        if type=="attempted" or type=="A" or type=="a":
            type="attempted"
        elif type=="validated" or type=="V" or type=="v":
            type="validated"
        elif type=="completed" or type=="C" or type=="c":
            type="completed"
        elif type=="combined" or type=="X" or type=="x":
            type="combined"
        else:
            raise ValueError("Transaction type not recognized")
        return self.database[robot_id][f"n_{type}_transactions"]


############################################################################################################
############################################################################################################
############################################################################################################
class PaymentSystem(ABC):
    @abstractmethod
    def new_transaction(self, transaction: Transaction, payment_api: PaymentAPI):
        pass

    @abstractmethod
    def new_reward(self, reward: float, payment_api:PaymentAPI, rewarded_id):
        pass


class DelayedPaymentPaymentSystem(PaymentSystem):
    def __init__(self, information_share):
        super().__init__()
        self.information_share = information_share
        self.transactions = set()


    def new_transaction(self, transaction: Transaction, payment_api: PaymentAPI):
        self.transactions.add(transaction)


    def new_reward(self, reward: float, payment_api, rewarded_id):
        reward_to_distribute = self.information_share * reward
        shares_mapping = self.calculate_shares_mapping(reward_to_distribute)
        for seller_id, share in shares_mapping.items():
            payment_api.transfer(rewarded_id, seller_id, share)
            last_redistribution= share-(self.stake_amount if hasattr(self,"stake_amount") else 0)
            payment_api.update_history(seller_id, last_redistribution)

        self.reset_transactions()


    def calculate_shares_mapping(self, reward_share_to_distribute):
        #TODO test
        #  if self.transaction:
        #   ...;return final_mapping
        #   return {}
        if len(self.transactions) == 0:
            return {}
        seller_ids = [t.seller_id for t in self.transactions]
        final_mapping = Counter(seller_ids)
        total_shares = sum(final_mapping.values())
        for seller in final_mapping:
            final_mapping[seller] = final_mapping[seller] * (
                reward_share_to_distribute) / total_shares
        return final_mapping


    def reset_transactions(self):
        self.transactions.clear()


class OutlierPenalisationPaymentSystem(PaymentSystem):
    def __init__(self, information_share):
        super().__init__()
        self.transactions = set()
        self.information_share = information_share
        self.pot_amount = 0
        self.stake_amount=1/25


    def new_transaction(self, transaction: Transaction, payment_api: PaymentAPI):
        payment_api.apply_cost(transaction.seller_id, self.stake_amount)
        self.pot_amount += self.stake_amount
        self.transactions.add(transaction)


    def new_reward(self, reward, payment_api:PaymentAPI, rewarded_id):
        reward_share_to_distribute = self.information_share * reward
        payment_api.apply_gains(rewarded_id, self.pot_amount)
        shares_mapping = self.calculate_shares_mapping(reward_share_to_distribute)

        for seller_id, share in shares_mapping.items():
            payment_api.transfer(rewarded_id, seller_id, share)
            last_redistribution= share-(self.stake_amount if hasattr(self,"stake_amount") else 0)
            payment_api.update_history(seller_id, last_redistribution)

        self.reset_transactions()


    def calculate_shares_mapping(self, reward_share_to_distribute):
        if len(self.transactions) == 0:
            return {}
        df_all = np.array([[t.seller_id, t.relative_angle, t.location, 0] for t in self.transactions])
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
            final_mapping[seller] = final_mapping[seller] * (
                    reward_share_to_distribute + self.pot_amount) / total_shares
        return final_mapping


    def reset_transactions(self):
        self.transactions.clear()
        self.pot_amount = 0