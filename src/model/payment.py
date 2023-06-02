from abc import ABC, abstractmethod
from collections import Counter
import numpy as np
import pandas as pd

import config as CONFIG_FILE
from helpers.utils import InsufficientFundsException
from model.navigation import Location

#turns off warning when working with on slices of DataFrames
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
        self.get_reward = payment_db.get_reward
        self.apply_gains = payment_db.apply_gains
        self.apply_cost = payment_db.apply_cost
        self.transfer = payment_db.transfer
        self.update_history = payment_db.update_history
        self.reputation_stake_coeff = payment_db.reputation_stake_coeff
        self.increment_stake = payment_db.increment_stake
        self.reset_stake = payment_db.reset_stake


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
        self.history_span=10
        self.database = {}
        for robot_id in population_ids:
            self.database[robot_id] = {"reward": payment_system_params["initial_reward"],
                                       #TODO introduce stake key only for correct payment system w/ staking
                                       "stake": {_: 0 for _ in population_ids},
                                       "payment_system": eval(payment_system_params['class'])(
                                                                **payment_system_params['parameters']),
                                        "wallet_age": 0,
                                        #TODO dict n_transactions would be cleaner
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

    #[ ] NEWCOMERS
    def add_newcomers(self, newcomers_ids,payment_system_params):
        NEW_DB_LEN=len(self.database)+len(newcomers_ids)
        for robot_id in self.database.keys():
            #TODO stake dictionary entries for new robots
            self.database[robot_id]["n_attempted_transactions"].extend([0]*len(newcomers_ids))
            self.database[robot_id]["n_validated_transactions"].extend([0]*len(newcomers_ids))
            self.database[robot_id]["n_completed_transactions"].extend([0]*len(newcomers_ids))
            self.database[robot_id]["n_combined_transactions" ].extend([0]*len(newcomers_ids))
        for robot_id in newcomers_ids:
            self.database[robot_id] = {"reward": payment_system_params["initial_reward"],
                                       "stake": {_: 0 for _ in range(NEW_DB_LEN) },
                                       "payment_system": eval(payment_system_params['class'])(
                                                                **payment_system_params['parameters']),
                                        "wallet_age": 0,
                                        "n_attempted_transactions": [0]*NEW_DB_LEN,
                                        "n_validated_transactions": [0]*NEW_DB_LEN,
                                        "n_completed_transactions": [0]*NEW_DB_LEN,
                                        "n_combined_transactions" : [0]*NEW_DB_LEN,
                                        "history": [None]*self.history_span,
                                    }


    def update_history(self,robot_id,redistribution):
        self.database[robot_id]["history"].pop(0)
        self.database[robot_id]["history"].append(redistribution)


    def reputation_stake_coeff(self,robot_id,reputation_method='h'):
        if reputation_method=='h':
            reputation=self.get_reputation(robot_id,method=reputation_method)
        elif reputation_method=='r' or reputation_method=='t':
            reputation=self.get_reputation(robot_id,method=reputation_method,verification_method='mean')
        # stake_ratio_0=1
        stake_ratio_min=0.5
        # stake_ratio_max=3
        if reputation is not None:
            #TODO requires tuning coeff for "r" reputation
            # POLYNOMIAL: higly penalizing/rewarding
            stake_ratio=stake_ratio_min**(2*reputation/self.history_span)
            # EXPONENTIAL: less penalizing/rewarding
            # stake_ratio=(stake_ratio_min+(stake_ratio_0-stake_ratio_min)*np.exp(-robot_reputation/history_len) \
            #                             -(stake_ratio_0-stake_ratio_max)*np.exp(-robot_reputation/history_len))/3
            # BY PARTS: non rewarding
            if reputation<0:
                stake_ratio=stake_ratio_min**(2*reputation/self.history_span)
                #NOTE: history_span is used in all cases to normalize reputation span
            else:
                '''#[ ] WEALTH TAXATION
                RICH_THRESHOLD=7
                if reputation>RICH_THRESHOLD:
                    stake_ratio=0.5*stake_ratio_min**(-reputation/self.history_span)
                # NO HIGHT REWARD PENALTY
                '''
                stake_ratio=1
                #'''
            return stake_ratio
        return 1
    

    def increment_stake(self,staker_id,buyer_id,amount):
        self.database[staker_id]["stake"][buyer_id]+=amount


    def reset_stake(self,staker_id,buyer_id):
        self.database[staker_id]["stake"][buyer_id]=0
        

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
            self.database[transaction.buyer_id]["payment_system"].new_transaction(transaction, PaymentAPI(self),
                                                                    # variable_stake=variable_stake,reputation_method=reputation_method
                                                                                  )
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
        #TODO integrate
        return sum([self.database[robot_id]["reward"] for robot_id in self.database])
        

    def get_reward(self, robot_id):
        #TODO integrate
        return self.database[robot_id]["reward"]

    #TODO PAYMENT SHOULD ONLY RETURN THE FULL LIST,
    #     COMPUTATION, EVEN MAX,MEAN,... SHOULD BE DONE BY THE CALLER
    def get_reputation(self, robot_id,method="reward",verification_method="discrete"):
        if method=="reward" or method=="r" or method=="R" or method=="w":
            if isinstance(robot_id,int):
                reward=self.get_reward(robot_id)
                if verification_method=="mean":
                    '''#[ ] HEURISTIC REPUTATION, works great
                    return reward-self.get_lowest_reward()*3
                    '''# NORMALIZED REPUTATION
                    # if reward>0:
                    #     bias_sign=1
                    # else:
                    #     bias_sign=-1
                    bias_sign=-1
                    reputation=reward+bias_sign*0.25*7500/self.database[robot_id]["wallet_age"]
                    return 1+10*np.tanh(reputation)
                    #'''
                return reward
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
            
        elif method=="total" or method=="t" or method=="T":#[ ]
            wealth=self.database[robot_id]["reward"]+\
                            sum(self.database[robot_id]["stake"].values())
            return wealth - self.get_lowest_reward()*3
        
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
        elif method=="total" or method=="t" or method=="T":#[ ]
            total_wealths=[self.database[robot_id]["reward"]+ 
                            sum(self.database[robot_id]["stake"].values()) \
                           for robot_id in self.database]
            return np.mean(total_wealths)
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
            or highest total wealth
        """
        if method=="reward" or method=="r" or method=="R" or method=="w":
            sorted_database = dict(sorted(self.database.items(), 
                                key=lambda x: x[1]["reward"], reverse=True))
        elif method=="total" or method=="t" or method=="T":
            new_db={}
            for robot_id in self.database:
                new_db[robot_id]=self.database[robot_id]["reward"]+\
                                sum(self.database[robot_id]["stake"].values())
            sorted_database = dict(sorted(new_db.items(),key=lambda x: x[1], reverse=True))
        return sorted_database
        
    
    def get_reward_ranking(self,robot_id,reputation_method):
        sorted_database = self.get_sorted_database(reputation_method)
        return list(sorted_database.keys()).index(robot_id)

    
    def get_reputation_ranking(self,robot_id,method="reward"):
        if method=="reward" or method=="r" or method=="R" or method=="w" or \
            method=="total" or method=="t" or method=="T":
            return self.get_reward_ranking(robot_id,method)
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
        # '''#[ ]DEFAULT MARKET
        #NOTE: DEFAULT as in market where default is possible
        if self.database[robot_id]["reward"] < cost:
            raise InsufficientFundsException#(robot_id)
        else:
            self.database[robot_id]["reward"] -= cost
        '''# NO DEFAULT MARKET
        self.database[robot_id]["reward"] -= cost
        #'''


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
    
    def get_stake_pot(self,robot_id:int):
        return self.database[robot_id]["payment_system"].pot_amount


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
    #TODO create params for each payment system
    def __init__(self, information_share,reputation_stake,reputation_metric):
        super().__init__()
        self.information_share = information_share
        self.transactions = set()


    def new_transaction(self, transaction: Transaction, payment_api: PaymentAPI):
        self.transactions.add(transaction)


    def new_reward(self, reward: float, payment_api, rewarded_id):
        reward_to_distribute = self.information_share * reward
        shares_mapping = self.calculate_shares_mapping(reward_to_distribute)
        try:
            for seller_id, share in shares_mapping.items():
                payment_api.transfer(rewarded_id, seller_id, share)
                last_redistribution= share-(self.stake_amount if hasattr(self,"stake_amount") else 0)
                payment_api.update_history(seller_id, last_redistribution)
        except InsufficientFundsException:
            pass
        finally:
            self.reset_transactions()


    def calculate_shares_mapping(self, reward_share_to_distribute=1):
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
    def __init__(self, information_share:float,reputation_stake:bool,reputation_metric:str):
        super().__init__()
        self.transactions = set()
        self.information_share = information_share
        self.pot_amount = 0
        self.stake_amount=1/25
        self.reputation_stake = reputation_stake
        self.reputation_metric = reputation_metric


    def get_stake_amount(self,payment_api:PaymentAPI,robot_id):
        stake_coeff=payment_api.reputation_stake_coeff(robot_id,self.reputation_metric) \
                    if self.reputation_stake else 1
        return stake_coeff*self.stake_amount
         

    def new_transaction(self, transaction: Transaction, payment_api: PaymentAPI):
        stake_amount=self.get_stake_amount(payment_api,transaction.seller_id)
        payment_api.apply_cost(transaction.seller_id, stake_amount)
        self.pot_amount += stake_amount
        self.transactions.add(transaction)
        payment_api.increment_stake(transaction.seller_id,transaction.buyer_id,stake_amount)


    def new_reward(self, reward, payment_api:PaymentAPI, rewarded_id):
        #'''#[ ] NORMAL DEFAULT: robot could cause IFE 
        reward_share_to_distribute = self.information_share * reward
        '''#DEFAULT PROTECTION: robot cannot cause IFE
        # reward_share_to_distribute=min(reward_share_to_distribute,payment_api.get_reward(rewarded_id))
        if reward_share_to_distribute<0: reward_share_to_distribute=0
        # '''
        payment_api.apply_gains(rewarded_id, self.pot_amount)
        
        shares_mapping = self.calculate_shares_mapping()
        try:
            for seller_id, share in shares_mapping.items():
                # ''' #[ ] DOUBLE TRANSFER
                payment_api.transfer(rewarded_id, seller_id, share*self.pot_amount)

            for seller_id, share in shares_mapping.items():
                payment_api.transfer(rewarded_id, seller_id, share*reward_share_to_distribute)
                '''#SINGLE TRANSFER
                payment_api.transfer(rewarded_id, seller_id, share*reward_share_to_distribute)
                #'''
                #[ ] POT-BIASED & REWARD BIASED REPUTATION: great performance improvement
                # last_redistribution= share*(self.pot_amount+reward_share_to_distribute)-(self.stake_amount if hasattr(self,"stake_amount") else 0)
                #UNBIASED REPUTATION #NOTE if reward<1, *reward will have a penalizing effect
                #NOTE_ could be reward scaled: w_x [*reward_share_to_distribute]
                # REWARD-SCALED BIASED
                # last_redistribution= share*reward_share_to_distribute-(self.stake_amount if hasattr(self,"stake_amount") else 0)
                # POT-BIASED ONLY
                # last_redistribution= share*self.pot_amount-(self.stake_amount if hasattr(self,"stake_amount") else 0)
                # UNBIASED
                last_redistribution= share- 1/len(shares_mapping)
                #TODO use current stake amount, base stake amount, or stake amount at the time of the transaction?
                # seller_stake_amount=self.get_stake_amount(payment_api,seller_id)#stake(t)k
                # seller_stake_amount=self.stake_amount#stake(0)
                #stake(k) for some past contribution k ???
                payment_api.update_history(seller_id, last_redistribution)
        except InsufficientFundsException:
            # CONFIG_FILE.IFE_COUNT+=1
            # print('IFE:PAY ', CONFIG_FILE.IFE_COUNT)
            pass
        finally:
            #TODO is it fair to just drop all the debts in case of IFE? ir this can be considered fairness?
            self.reset_transactions()
            for seller_id, _ in shares_mapping.items():
                payment_api.reset_stake(seller_id,rewarded_id)

    
    def calculate_shares_mapping(self,amount_to_distribute=1):
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
            final_mapping[seller] = final_mapping[seller] * amount_to_distribute / total_shares
        return final_mapping


    def reset_transactions(self):
        self.transactions.clear()
        self.pot_amount = 0