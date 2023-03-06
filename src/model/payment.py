from abc import ABC, abstractmethod
from collections import Counter

import numpy as np

from helpers.utils import InsufficientFundsException
from model.navigation import Location
import pandas as pd

pd.options.mode.chained_assignment = None


class Transaction:
    def __init__(self, buyer_id, seller_id, location, info_relative_angle, timestep):
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.location = location
        self.relative_angle = info_relative_angle
        self.timestep = timestep


class PaymentSystem(ABC):

    @abstractmethod
    def new_transaction(self, transaction: Transaction, payment_api):
        pass

    @abstractmethod
    def new_reward(self, reward: float, payment_api, rewarded_id):
        pass


class DelayedPaymentPaymentSystem(PaymentSystem):

    def __init__(self, information_share):
        super().__init__()
        self.information_share = information_share
        self.transactions = set()

    def new_transaction(self, transaction: Transaction, payment_api):
        self.transactions.add(transaction)

    def new_reward(self, reward: float, payment_api, rewarded_id):
        reward_to_distribute = self.information_share * reward
        shares_mapping = self.calculate_shares_mapping(reward_to_distribute)
        for seller_id, share in shares_mapping.items():
            payment_api.transfer(rewarded_id, seller_id, share)

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

    def new_transaction(self, transaction: Transaction, payment_api):
        stake_amount = 1 / 25
        payment_api.apply_cost(transaction.seller_id, stake_amount)
        self.pot_amount += stake_amount
        self.transactions.add(transaction)

    def new_reward(self, reward, payment_api, rewarded_id):
        reward_share_to_distribute = self.information_share * reward
        payment_api.apply_gains(rewarded_id, self.pot_amount)
        shares_mapping = self.calculate_shares_mapping(reward_share_to_distribute)
        for seller_id, share in shares_mapping.items():
            payment_api.transfer(rewarded_id, seller_id, share)

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


class PaymentAPI:
    def __init__(self, payment_db):
        self.apply_gains = payment_db.apply_gains
        self.apply_cost = payment_db.apply_cost
        self.transfer = payment_db.transfer


class PaymentDB:
    """
    data stored on the blockchain:
    - reward (float): the amount of reward the robot has at the moment;
    - payment_system (PaymentSystem): the payment system used by the robot;
    - age (int): the age of the robot, exoressed in number of ticks;
    - n_transactions (int): the number of transactions the robot has done;
    - reward_trend (?): the trend of the reward of the robot. Could be expressed
        qith derivative, difference or sign of the difference;
    - n_transactions_trend (?): the trend of the number of transactions of the robot.
    """
    def __init__(self, population_ids, payment_system_params):
        self.nb_transactions = 0
        self.database = {}
        #TODO which is the best one?
        # self.log_db=set()
        # self.log_db=""
        self.log_db=[]
        # self.info_share = info_share
        for robot_id in population_ids:
            self.database[robot_id] = {"reward": payment_system_params["initial_reward"],
                                       "payment_system": eval(payment_system_params['class'])(
                                                **payment_system_params['parameters']),
                                        "age": 0,
                                        "n_transactions": 0,
                                        "reward_trend": 0,
                                        "n_transactions_trend": 0,
                                }


    def pay_reward(self, robot_id, reward=1):
        self.database[robot_id]["reward"] += reward


    def transfer(self, from_id, to_id, amount):
        if amount < 0:
            raise ValueError("Amount must be positive")
        self.apply_cost(from_id, amount)
        self.apply_gains(to_id, amount)


    def record_transaction(self, transaction: Transaction):
        self.nb_transactions += 1
        self.database[transaction.buyer_id]["payment_system"].new_transaction(transaction, PaymentAPI(self))
        self.log_transaction(transaction)


    def pay_creditors(self, debitor_id, total_reward=1):
        self.database[debitor_id]["payment_system"].new_reward(total_reward, PaymentAPI(self),
                                                               debitor_id)


    def get_reward(self, robot_id):
        return self.database[robot_id]["reward"]


    def get_highest_reward(self):
        return np.max([self.database[robot_id]["reward"] for robot_id in self.database])


    def get_lowest_reward(self):
        return np.min([self.database[robot_id]["reward"] for robot_id in self.database])

    
    def get_average_reward(self):
        return np.average([self.database[robot_id]["reward"] for robot_id in self.database])

        
    def apply_cost(self, robot_id, cost):
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


    def log_transaction(self,transaction:Transaction):
        # self.log_db.add(transaction)
        # self.log_db+=f"buyer:{transaction.buyer_id}, seller:{transaction.seller_id}, at:{transaction.timestep}"\
        #                "#####################\n"
        self.log_db.append([transaction.timestep,transaction.buyer_id,transaction.seller_id])


    # def get_database(self):
    #     return self.database, self.log_db
