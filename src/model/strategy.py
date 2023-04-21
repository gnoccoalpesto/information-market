import copy
from abc import ABC, abstractmethod

from model.navigation import Target,Location
from model.payment import PaymentDB


def strategy_factory(strategy):
    strategy=eval(strategy)()
    return strategy
    
class PurchasedTarget:
    def __init__(self):
        self.age = None
        self.relative_distance = None

    def get_age(self):
        return self.age
    
    def set_age(self,age):
        self.age = age

    def get_distance(self):
        return self.relative_distance

    def set_distance(self,distance):
        self.relative_distance = distance

    def update(self,dr):
        self.age+=1
        self.relative_distance -= dr
    

class InformationStrategy(ABC):
    @abstractmethod
    def should_combine(self, my_target: Target, other_target: Target):
        """Whether a robot's target information should be replaced/combined with another"""

    @abstractmethod
    def combine(self, my_target: Target, other_target: Target, bots_distance) -> Target:
        """Combine a robot's target information with other information"""


class BetterAgeStrategy(InformationStrategy):
    def should_combine(self, my_target: Target, other_target: Target):
        return my_target.age > other_target.age

    def combine(self, my_target: Target, other_target: Target, bots_distance) -> Target:
        new_target = copy.deepcopy(other_target)
        new_target.set_distance(new_target.get_distance() + bots_distance)
        return new_target


#BEST
class WeightedAverageAgeStrategy(InformationStrategy):
    def should_combine(self, my_target: Target, other_target: Target):
        if other_target.valid and my_target.age > other_target.age:
            return True
        return False

    #TODO remove distance, since added outside and passing identically zero
    def combine(self, my_target: Target, other_target: Target, bots_distance) -> Target:
        new_target = copy.deepcopy(other_target)
        ages_sum = my_target.age + other_target.age
        new_distance = (my_target.age / ages_sum) * (other_target.get_distance() + bots_distance) + (
                other_target.age / ages_sum) * my_target.get_distance()  # older = lower weight
        if not my_target.is_valid():
            new_distance = other_target.get_distance() + bots_distance
        new_target.set_distance(new_distance)
        new_target.age = ages_sum // 2
        return new_target


#HALFWAY DECENT
class NewRunningWeightedAverageReputationStrategy(InformationStrategy):
    def should_combine(self, _ , other_target: Target):
        if other_target.is_valid():
            return True
        return False

    def combine(self, my_target: Target, other_target: Target, mean_reputation, seller_reputation) -> Target:
        new_target = copy.deepcopy(other_target)
        reputation_ratio=seller_reputation/(mean_reputation*0.4)
        reputation_sum=1+reputation_ratio

        if not my_target.is_valid():
            new_distance = other_target.get_distance()
        else:
            new_distance=(my_target.get_distance()/reputation_sum +other_target.get_distance()*reputation_ratio/reputation_sum)

        new_age=(my_target.get_age()/reputation_sum+other_target.get_age()*seller_reputation/reputation_sum)
        new_target.set_distance(new_distance)
        new_target.set_age(new_age)
        return new_target


#TRASH
class WeightedAverageReputationAgeStrategy(InformationStrategy):
    def should_combine(self, my_target: Target, other_target: Target):
        if other_target.valid and my_target.age > other_target.age:
            return True
        return False
        
    def combine(self, my_target: Target, other_target: Target, bots_distance, mean_reputation, seller_reputation) -> Target:
        new_target = copy.deepcopy(other_target)
        ages_sum = my_target.age + other_target.age
        reputation_ratio=seller_reputation/mean_reputation
        reputation_sum=1+reputation_ratio
        new_distance = (my_target.age / (reputation_sum*ages_sum)) * (other_target.get_distance() + bots_distance) + \
             ((other_target.age * reputation_ratio) / (reputation_sum*ages_sum)) * my_target.get_distance()  
        if not my_target.is_valid():
            new_distance = other_target.get_distance() + bots_distance
        new_target.set_distance(new_distance)
        new_target.age = ages_sum // 2
        return new_target


#TRASH
class FullWeightedAverageReputationStrategy(InformationStrategy):
    def __init__(self):
        self.initialized=False

    def initialize(self,robots_amount):
        self.purchased_targets = {
            Location.NEST:{robot_id:PurchasedTarget() for robot_id in range(robots_amount)},
            Location.FOOD:{robot_id:PurchasedTarget() for robot_id in range(robots_amount)}
            }
        self.initialized=True

    def should_combine(self, _, other_target: Target,seller_id):
        #combines if other_target is valid and younger than the one stored in memory
        if other_target.is_valid() and\
            self.purchased_targets[other_target.location][seller_id].get_age() > other_target.get_age():
            return True
        return False

    def combine(self, my_target: Target, other_target: Target, my_id, seller_id, payment_database:PaymentDB) -> Target:
        #TODO: is passing all bchain inefficient? maybe better to just pass the vector (but must call outside to know 
        #   purchase locations for the IDs then)
        if not self.initialized:
            self.initialize(payment_database.get_number_of_wallets())
        
        if self.purchased_targets[other_target.location][seller_id].get_age() is None or \
                other_target.get_age()<self.purchased_targets[other_target.location][seller_id].get_age():
            self.purchased_targets[other_target.location][seller_id].set_age(other_target.get_age())
            self.purchased_targets[other_target.location][seller_id].set_distance(other_target.get_distance())
        
        my_reputation=payment_database.get_reward(my_id)
        sellers_reputation=[payment_database.get_reward(purchased_id) 
                        for purchased_id in self.purchased_targets[other_target.location]]
        
        new_target=copy.deepcopy(other_target)
        purchased_distance_list=[self.purchased_targets[other_target.location][purchased_id].get_distance()
                         for purchased_id in self.purchased_targets[other_target.location]]
        purchased_ages_list=[self.purchased_targets[other_target.location][purchased_id].get_age()
                            for purchased_id in self.purchased_targets[other_target.location]]

        if not my_target.is_valid():
            new_distance = other_target.get_distance()
        else:
            new_distance=(my_reputation/sum(sellers_reputation+[my_reputation])) *my_target.get_distance()+\
                sum([(seller_reputation/sum(sellers_reputation+[my_reputation]))*target\
                for seller_reputation,target in zip(sellers_reputation,purchased_distance_list) if target is not None])

        average_age=(my_reputation/sum(sellers_reputation+[my_reputation])) *my_target.get_age()+\
                sum([(seller_reputation/sum(sellers_reputation+[my_reputation/sum(sellers_reputation+[my_reputation])]))*age\
                for seller_reputation,age in zip(sellers_reputation,purchased_ages_list) if age is not None])

        new_target.set_distance(new_distance)
        new_target.set_age(average_age)
        return new_target

    def update_purchases(self,my_id,dr):
        for location in self.purchased_targets:
            for purchased_id in self.purchased_targets[location]:
                self.purchased_targets[location][purchased_id].update(dr)


#TRASH
class NewFullWeightedAverageReputationStrategy(InformationStrategy):
    def __init__(self):
        self.initialized=False


    def initialize(self,robots_amount):
        self.purchased_targets = {
            Location.NEST:{robot_id:PurchasedTarget() for robot_id in range(robots_amount)},
            Location.FOOD:{robot_id:PurchasedTarget() for robot_id in range(robots_amount)}
            }
        self.initialized=True


    def should_combine(self, _, other_target: Target,seller_id):
        if other_target.is_valid() and\
            self.purchased_targets[other_target.location][seller_id].get_age() > other_target.get_age():
            return True
        return False


    def combine(self, my_target: Target, other_target: Target, seller_id, payment_database:PaymentDB) -> Target:
        if not self.initialized:
            self.initialize(payment_database.get_number_of_wallets())

        if self.purchased_targets[other_target.location][seller_id].get_age() is None or \
                other_target.get_age()<self.purchased_targets[other_target.location][seller_id].get_age():
            self.purchased_targets[other_target.location][seller_id].set_age(other_target.get_age())
            self.purchased_targets[other_target.location][seller_id].set_distance(other_target.get_distance())
        
        mean_reputation=payment_database.get_mean_reputation('w')
        sellers_reputation=[payment_database.get_reward(purchased_id) 
                        for purchased_id in self.purchased_targets[other_target.location]]
        sellers_ratios=sellers_reputation/mean_reputation
        
        new_target=copy.deepcopy(other_target)

        purchased_distance_list=[self.purchased_targets[other_target.location][purchased_id].get_distance()
                         for purchased_id in self.purchased_targets[other_target.location]]
        purchased_ages_list=[self.purchased_targets[other_target.location][purchased_id].get_age()
                            for purchased_id in self.purchased_targets[other_target.location]]

        if not my_target.is_valid():
            new_distance = other_target.get_distance()
        else:
            new_distance=(1/sum(sellers_ratios+[1])) *my_target.get_distance()+\
                sum([(sellers_ratio/sum(sellers_ratios+[1]))*target\
                for sellers_ratio,target in zip(sellers_reputation,purchased_distance_list) if target is not None])

        average_age=(1/sum(sellers_ratios+[1])) *my_target.get_age()+\
                sum([(sellers_ratio/sum(sellers_ratios+[1]))*age\
                for sellers_ratio,age in zip(sellers_reputation,purchased_ages_list) if age is not None])

        new_target.set_distance(new_distance)
        new_target.set_age(average_age)
        return new_target

    def update_purchases(self,my_id,dr):
        for location in self.purchased_targets:
            for purchased_id in self.purchased_targets[location]:
                self.purchased_targets[location][purchased_id].update(dr)


class DecayingQualityStrategy(InformationStrategy):
    def should_combine(self, my_target: Target, other_target: Target):
        if other_target.is_valid() and other_target.decaying_quality > my_target.decaying_quality:
            return True
        return False

    def combine(self, my_target: Target, other_target: Target, bots_distance) -> Target:
        new_target = copy.deepcopy(other_target)
        new_target.set_distance(new_target.get_distance() + bots_distance)
        return new_target


class WeightedDecayingQualityStrategy(DecayingQualityStrategy):
    def combine(self, my_target: Target, other_target: Target, bots_distance) -> Target:
        new_target = copy.deepcopy(other_target)
        qualities_sum = my_target.decaying_quality + other_target.decaying_quality
        new_distance = (my_target.decaying_quality / qualities_sum) * my_target.get_distance() + (
                other_target.decaying_quality / qualities_sum) * (other_target.get_distance() + bots_distance)
        if not my_target.is_valid():
            new_distance = other_target.get_distance() + bots_distance
        new_target.set_distance(new_distance)
        new_target.decaying_quality = other_target.decaying_quality
        return new_target
