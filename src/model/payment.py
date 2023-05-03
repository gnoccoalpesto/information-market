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
        self.stake_amount = payment_db.stake_amount


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
                                        "n_validated_transactions": [0]*len(population_ids),
                                        "n_completed_transactions": [0]*len(population_ids),
                                        "n_combined_transactions" : [0]*len(population_ids),
                                        "history": [None]*self.history_span, #NOTE history is loaded bottom->top
                                        # "reward_trend": 0,
                                        # "n_transactions_trend": 0,
                                        # LOCATIONS COULD PUT TOO MUCH STRESS <- CONTINUOUS UPDATE
                                        #->TODO COULD USE A DATE INSTEAD
                                        # "locations_acquisition": {Location.FOOD: 0,
                                        #                  Location.NEST: 0
                                        #                 }
                                    }
        self.completed_transactions_log=[]

    #[ ] 
    def add_newcomers(self, newcomers_ids,payment_system_params):
        for robot_id in newcomers_ids:
            self.database[robot_id] = {"reward": payment_system_params["initial_reward"],
                                       "payment_system": eval(payment_system_params['class'])(
                                                                **payment_system_params['parameters']),
                                        "wallet_age": 0,
                                        "n_attempted_transactions": [0]*(len(self.database)+len(newcomers_ids)),
                                        "n_validated_transactions": [0]*(len(self.database)+len(newcomers_ids)),
                                        "n_completed_transactions": [0]*(len(self.database)+len(newcomers_ids)),
                                        "n_combined_transactions" : [0]*(len(self.database)+len(newcomers_ids)),
                                        "history": [None]*self.history_span,
                                    }
        for robot_id in self.database.keys():
            self.database[robot_id] = {
                                        "n_attempted_transactions": self.database[robot_id]["n_attempted_transactions"]+[0]*len(newcomers_ids),
                                        "n_validated_transactions": self.database[robot_id]["n_validated_transactions"]+[0]*len(newcomers_ids),
                                        "n_completed_transactions": self.database[robot_id]["n_completed_transactions"]+[0]*len(newcomers_ids),
                                        "n_combined_transactions" : self.database[robot_id]["n_combined_transactions"]+[0]*len(newcomers_ids),
                                    }


    def update_history(self,robot_id,redistribution):
        self.database[robot_id]["history"].pop(0)
        self.database[robot_id]["history"].append(redistribution)

    #[ ]
    def stake_amount(self,stake_amount,robot_id):
        robot_reputation=self.get_reputation(robot_id,method='h')
        # stake_ratio_0=1
        stake_ratio_min=0.5
        # stake_ratio_max=3
        history_len=10
        if CONFIG_FILE.REPUTATION_STAKE and robot_reputation is not None:
            stake_ratio=stake_ratio_min**(2*robot_reputation/history_len)
            # stake_ratio=(stake_ratio_min+(stake_ratio_0-stake_ratio_min)*np.exp(-robot_reputation/history_len) \
            #                             -(stake_ratio_0-stake_ratio_max)*np.exp(-robot_reputation/history_len))/3
            
            return stake_amount*stake_ratio
        return stake_amount
        

    def get_history(self,robot_id):
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
        elif type=="validated" or type=="V" or type=="v":
            self.database[buyer_id]["n_validated_transactions"][seller_id] += 1
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

    #TODO PAYMENT SHOULD ONLY RETURN THE FULL LIST,
    #     COMPUTATION, EVEN MAX,MEAN,... SHOULD BE DONE BY THE CALLER
    def get_reputation(self, robot_id,method="reward",verification_method="discrete"):
        if method=="reward" or method=="r" or method=="R" or method=="w":
            if isinstance(robot_id,int):
                return self.get_reward(robot_id)
            elif robot_id=="all":
                return self.get_total_reward()
            elif robot_id=="mean":
                return self.get_mean_reward()
            elif robot_id=="max":
                return self.get_highest_reward()
            elif robot_id=="min":
                return self.get_lowest_reward()
            else:
                raise ValueError("Robot id not recognized")

        elif method=="history" or method=="h" or method=="H":
            method="history"
            if isinstance(robot_id,int):
                valid_history=[h for h in self.database[robot_id]["history"]
                                if h is not None]
                if len(valid_history)>0:
                    reputation=0
                    for i,h in enumerate(valid_history):
                        if verification_method=="discrete":
                            increment=np.sign(h)
                        elif verification_method=="difference":
                            increment=h
                        elif verification_method=="recency":
                            increment=h*(i+1)
                        elif verification_method=="aged":
                            increment=h/(len(valid_history)-i)
                        elif verification_method=="aged2":
                            increment=h/(len(valid_history)-i)**2
                        reputation+=increment

                    return reputation
                return None
            elif robot_id=="all":
                return None
            elif robot_id=="mean":
                return self.get_mean_reputation(method,verification_method)
            elif robot_id=="max":
                return self.get_highest_reputation(method,verification_method)
            elif robot_id=="min":
                return self.get_lowest_reputation(method,verification_method)
            else:
                raise ValueError("Robot id not recognized")

    def get_mean_reputation(self,method="reward",verification_method="discrete"):
        if method=="reward" or method=="r" or method=="R" or method=="w":
            return self.get_mean_reward()
        elif method=="history" or method=="h" or method=="H":
            method="history"
            reputations=[self.get_reputation(robot_id,method,verification_method) for robot_id in self.database ]
            valid_reputations=[r for r in reputations if r is not None]
            return np.mean([r for r in valid_reputations]) if len(valid_reputations)>0 else None

    def get_highest_reputation(self,method="reward",verification_method="discrete"):
        if method=="reward" or method=="r" or method=="R" or method=="w":
            return self.get_highest_reward()
        elif method=="history" or method=="h" or method=="H":
            method="history"
            reputations=[self.get_reputation(robot_id,method,verification_method) for robot_id in self.database ]
            valid_reputations=[r for r in reputations if r is not None]
            return np.max([r for r in valid_reputations]) if len(valid_reputations)>0 else None

    def get_lowest_reputation(self,method="reward",verification_method="difference"):
        if method=="reward" or method=="r" or method=="R" or method=="w":
            return self.get_lowest_reward()
        elif method=="history" or method=="h" or method=="H":
            method="history"
            reputations=[self.get_reputation(robot_id,method,verification_method) for robot_id in self.database ]
            valid_reputations=[r for r in reputations if r is not None]
            return np.min([r for r in valid_reputations]) if len(valid_reputations)>0 else None

    def get_highest_reward(self):
        return np.max([self.database[robot_id]["reward"] for robot_id in self.database])

    def get_lowest_reward(self):
        return np.min([self.database[robot_id]["reward"] for robot_id in self.database])
    
    def get_mean_reward(self):
        return np.average([self.database[robot_id]["reward"] for robot_id in self.database])


    def get_sorted_database(self,method="reward"):
        """
        returns blockchain (dict), sorted by highest reward first
        """
        if method=="reward" or method=="r" or method=="R" or method=="w":
            sorted_database = dict(sorted(self.database.items(), 
                                key=lambda x: x[1]["reward"], reverse=True))
        return sorted_database
        
    
    def get_reward_ranking(self,robot_id):
        #TODO remove?
        sorted_database = self.get_sorted_database()
        return list(sorted_database.keys()).index(robot_id)

    
    def get_reputation_ranking(self,robot_id,method="reward"):
        #TODO remove?
        if method=="reward" or method=="r" or method=="R" or method=="w":
            return self.get_reward_ranking(robot_id)
        elif method=="history" or method=="h" or method=="H":
                reputations=[self.get_reputation(robot_id,method="history") for robot_id in self.database]
                valid_reputations=[r for r in reputations if r is not None]
                return valid_reputations[np.argmax(valid_reputations)] if len(valid_reputations)>0 else None
                    

    def get_number_of_wallets(self):
        return len(self.database)


    def apply_cost(self, robot_id, cost):
        '''cost of motion, stopping,recharge, etc.'''
        if cost < 0:
            raise ValueError("Cost must be positive")
        if self.database[robot_id]["reward"] < cost:
            #BUG outer except cannot catch this
            # conditions: P, any behav, initial_reward=1, share=0.5, berry_reward=1
            #generated by:
            # check_location-> deposit_food -> pay_creditors -> new_reward ->
            #    transfer-> apply_cost -> InsufficientFundsException
            #TODO test NOT GENERATED BY BUY (FOR NOW)
            # if test: handle the exception locally, else...
            # raise InsufficientFundsException(robot_id)
            pass
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

            last_redistribution= share
            payment_api.update_history(seller_id, last_redistribution)

        self.reset_transactions()


    def calculate_shares_mapping(self, reward_share_to_distribute):
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

#[ ]
    def get_stake_amount(self,payment_api:PaymentAPI,robot_id):
        return payment_api.stake_amount(self.stake_amount,robot_id)
         

    def new_transaction(self, transaction: Transaction, payment_api: PaymentAPI):
        stake_amount=self.get_stake_amount(payment_api,transaction.seller_id)
        payment_api.apply_cost(transaction.seller_id, stake_amount)
        self.pot_amount += stake_amount
        self.transactions.add(transaction)


    def new_reward(self, reward, payment_api:PaymentAPI, rewarded_id):
        #[ ] originally: payment_api.apply_gains(rewarded_id, self.pot_amount)
        reward_share_to_distribute = self.information_share * reward + self.pot_amount
        shares_mapping = self.calculate_shares_mapping(reward_share_to_distribute)
        for seller_id, share in shares_mapping.items():
            payment_api.transfer(rewarded_id, seller_id, share)

            #TODO use current stake amount, base stake amount, or stake amount at the time of the transaction?
            # seller_stake_amount=self.get_stake_amount(payment_api,seller_id)#stake(t)k
            seller_stake_amount=self.stake_amount#stake(0)
            #stake(k) for some past contribution k ???
            last_redistribution= share-seller_stake_amount #if hasattr(self,"stake_amount") else 0)
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
                    #[ ] originally:  reward_share_to_distribute + self.pot_amount) / total_shares
                    reward_share_to_distribute) / total_shares
        return final_mapping


    def reset_transactions(self):
        self.transactions.clear()
        self.pot_amount = 0