import copy
from abc import ABC, abstractmethod
from enum import Enum
from math import cos, radians, sin
import numpy as np

from model.payment import PaymentDB
from model.communication import CommunicationSession
from model.navigation import Location, NavigationTable
from model.strategy import WeightedAverageAgeStrategy
from helpers.utils import get_orientation_from_vector, norm, InsufficientFundsException, \
    NoInformationSoldException, NoLocationSensedException


class State(Enum):
    EXPLORING = 1
    SEEKING_FOOD = 2
    SEEKING_NEST = 3


class RequiredInformation(Enum):
    """
    This class characterizes the information required
    local: Naive, scepticals, scaboteurs
    global: uses wealth reputataion
    """
    LOCAL = 0
    GLOBAL = 1



def behavior_factory(behavior_params):
    behavior = eval(behavior_params['class'])(**behavior_params['parameters'])
    return behavior


class Behavior(ABC):
    def __init__(self):
        self.color = "blue"
        self.navigation_table = NavigationTable()

    @abstractmethod
    def buy_info(self, neighbors):
        pass

    @abstractmethod
    def step(self, api):
        """Simulates 1 step of behavior (= 1 movement)"""

    @abstractmethod
    def sell_info(self, location):
        pass

    def debug_text(self):
        return ""


class NaiveBehavior(Behavior):
    def __init__(self):
        super().__init__()
        self.state = State.EXPLORING
        self.strategy = WeightedAverageAgeStrategy()
        self.dr = np.array([0, 0]).astype('float64')
        self.id = -1
        self.required_information = RequiredInformation.LOCAL


    def buy_info(self,_, session: CommunicationSession):
        for location in Location:
            metadata = session.get_metadata(location)
            metadata_sorted_by_age = sorted(metadata.items(), key=lambda item: item[1]["age"])
            for bot_id, data in metadata_sorted_by_age:
                session.record_attempted_transaction()

                if data["age"] < self.navigation_table.get_age_for_location(location):
                    session.record_validated_transaction()

                    try:
                        other_target = session.make_transaction(neighbor_id=bot_id, location=location)
                        new_target = self.strategy.combine(self.navigation_table.get_information_entry(location),
                                                           other_target,
                                                           session.get_distance_from(bot_id))
                        session.record_combined_transaction()
                        self.navigation_table.replace_information_entry(location, new_target)
                        break
                    except InsufficientFundsException:
                        pass
                    except NoInformationSoldException:
                        pass


    def step(self, api):
        self.dr[0], self.dr[1] = 0, 0
        self.id = api.get_id()
        sensors = api.get_sensors()
        self.update_behavior(sensors, api)
        self.update_movement_based_on_state(api)
        self.check_movement_with_sensors(sensors)
        self.update_nav_table_based_on_dr()


    def sell_info(self, location):
        return self.navigation_table.get_information_entry(location)


    def update_behavior(self, sensors, api):
        for location in Location:
            if sensors[location]:
                try:
                    self.navigation_table.set_relative_position_for_location(location,
                                                                             api.get_relative_position_to_location(
                                                                                 location))
                    self.navigation_table.set_information_valid_for_location(location, True)
                    self.navigation_table.set_age_for_location(location, 0)
                except NoLocationSensedException:
                    print(f"Sensors do not sense {location}")

        if self.state == State.EXPLORING:
            if self.navigation_table.is_information_valid_for_location(Location.FOOD) and not api.carries_food():
                self.state = State.SEEKING_FOOD
            if self.navigation_table.is_information_valid_for_location(Location.NEST) and api.carries_food():
                self.state = State.SEEKING_NEST

        elif self.state == State.SEEKING_FOOD:
            if api.carries_food():
                if self.navigation_table.is_information_valid_for_location(Location.NEST):
                    self.state = State.SEEKING_NEST
                else:
                    self.state = State.EXPLORING
            elif norm(self.navigation_table.get_relative_position_for_location(Location.FOOD)) < api.radius():
                self.navigation_table.set_information_valid_for_location(Location.FOOD, False)
                self.state = State.EXPLORING

        elif self.state == State.SEEKING_NEST:
            if not api.carries_food():
                if self.navigation_table.is_information_valid_for_location(Location.FOOD):
                    self.state = State.SEEKING_FOOD
                else:
                    self.state = State.EXPLORING
            elif norm(self.navigation_table.get_relative_position_for_location(Location.NEST)) < api.radius():
                self.navigation_table.set_information_valid_for_location(Location.NEST, False)
                self.state = State.EXPLORING

        if sensors["FRONT"]:
            if self.state == State.SEEKING_NEST:
                self.navigation_table.set_information_valid_for_location(Location.NEST, False)
                self.state = State.EXPLORING
            elif self.state == State.SEEKING_FOOD:
                self.navigation_table.set_information_valid_for_location(Location.FOOD, False)
                self.state = State.EXPLORING


    def update_movement_based_on_state(self, api):
        if self.state == State.SEEKING_FOOD:
            self.dr = self.navigation_table.get_relative_position_for_location(Location.FOOD)
            food_norm = norm(self.navigation_table.get_relative_position_for_location(Location.FOOD))
            if food_norm > api.speed():
                self.dr = self.dr * api.speed() / food_norm

        elif self.state == State.SEEKING_NEST:
            self.dr = self.navigation_table.get_relative_position_for_location(Location.NEST)
            nest_norm = norm(self.navigation_table.get_relative_position_for_location(Location.NEST))
            if nest_norm > api.speed():
                self.dr = self.dr * api.speed() / nest_norm

        else:
            turn_angle = api.get_levi_turn_angle()
            self.dr = api.speed() * np.array([cos(radians(turn_angle)), sin(radians(turn_angle))])

        api.set_desired_movement(self.dr)


    def check_movement_with_sensors(self, sensors):
        if (sensors["FRONT"] and self.dr[0] >= 0) or (sensors["BACK"] and self.dr[0] <= 0):
            self.dr[0] = -self.dr[0]
        if (sensors["RIGHT"] and self.dr[1] <= 0) or (sensors["LEFT"] and self.dr[1] >= 0):
            self.dr[1] = -self.dr[1]


    def update_nav_table_based_on_dr(self):
        self.navigation_table.update_from_movement(self.dr)
        self.navigation_table.rotate_from_angle(-get_orientation_from_vector(self.dr))


class ReputationWealthBehaviour(NaiveBehavior):
    def __init__(self):
        super(ReputationWealthBehaviour, self).__init__()
        #TODO if reputation level raises, has pending info sense?
        # self.pending_information = {location: {} for location in Location}
        self.required_information=RequiredInformation.GLOBAL


    @abstractmethod
    def verify_reputation(self,payment_database:PaymentDB, session: CommunicationSession, bot_id):
        pass

    def get_reputation_score(self, payment_database:PaymentDB, bot_id):
        return payment_database.get_reward(bot_id)

    def buy_info(self, session: CommunicationSession, payment_database: PaymentDB):
        for location in Location:
            metadata = session.get_metadata(location)
            metadata_sorted_by_age = sorted(metadata.items(), key=lambda item: item[1]["age"])
            for bot_id, data in metadata_sorted_by_age:
                if data["age"] < self.navigation_table.get_age_for_location(location):
                    #  and bot_id not in self.pending_information[location]:
                    try:
                        other_target = session.make_transaction(neighbor_id=bot_id, location=location)
                        other_target.set_distance(other_target.get_distance() + session.get_distance_from(
                            bot_id))

                        if not self.navigation_table.is_information_valid_for_location(location) or \
                                self.verify_reputation(payment_database,session, bot_id):
                            new_target = self.strategy.combine(self.navigation_table.get_information_entry(location),
                                                               other_target,
                                                               np.array([0, 0]))
                            self.navigation_table.replace_information_entry(location, new_target)
                            # self.pending_information[location].clear()
                    except InsufficientFundsException:
                        pass
                    except NoInformationSoldException:
                        pass
    def step(self, api):
        return super().step(api)


class ReputationTresholdBehaviour(ReputationWealthBehaviour):
    def __init__(self):
        super(ReputationTresholdBehaviour, self).__init__()
        #TODO if reputation level raises, has pending info sense?
        # self.pending_information = {location: {} for location in Location}

    @abstractmethod
    #TODO
    # def get_threshold_value(self, session: CommunicationSession):
    def get_threshold_value(self):
        pass

    def verify_reputation(self,payment_database:PaymentDB, session: CommunicationSession, bot_id):
        # return self.get_reputation_score(session, bot_id) >\
        return self.get_reputation_score(payment_database, bot_id) >\
                 self.get_threshold_value(payment_database, session)


class ReputationStaticThresholdBehavior(ReputationTresholdBehaviour):
    def __init__(self,threshold=1):
        super(ReputationStaticThresholdBehavior, self).__init__()
        self.reputation_threshold=threshold

    def get_threshold_value(self, payment_database:PaymentDB,session: CommunicationSession):
            return self.reputation_threshold


class ReputationDynamicThresholdBehavior(ReputationTresholdBehaviour):
    def __init__(self,comparison_method="allmax",scaling=1):
        super(ReputationDynamicThresholdBehavior, self).__init__()
        self.comparison_method=comparison_method
        self.scaling=scaling

    def get_threshold_value(self, payment_database:PaymentDB,session: CommunicationSession):
        """
        allmax: selects only above a certain percentage of maximum wealth (wealthiest bots), of all robots
        allavg:selects only above certain percentage of average wealth, considering all robots
        allmin: selects only above a certain percentage of minimum wealth (poorest bots), of all robots
        TODO: all_rise:  selects above a certaint value, increasing with time, starting from a certain level, of all robots

        DEPRECATED:
        neighmax: selects only above a certain percentage of maximum wealth (wealthiest bots), of neighbors
        neighavg: selects only above certain percentage of average wealth, considering neighbors
        neighmin: selects only above a certain percentage of minimum wealth (poorest bots), of neighbors
        """
        # extension, metric=re.split("_",self.comparison_method)
        extension, metric=self.comparison_method[:-3],self.comparison_method[-3:]
        reputation_dict = {"all":{
                                "max":payment_database.get_highest_reward,
                                 "avg":payment_database.get_average_reward,
                                 "min":payment_database.get_lowest_reward,
                                 },
                            "neigh":{
                                    "max":session.get_max_neighboor_reward,
                                    "avg":session.get_average_neighbor_reward,
                                    "min":session.get_min_neighboor_reward,
                                }
                            }
        try:
            return self.scaling*reputation_dict[extension][metric]()
        except KeyError:
            exit(1)
            # return super().reputation_threshold(session, self.method)


class ScepticalReputationBehavior(NaiveBehavior):
    def __init__(self,comparison_method="allavg",scaling=1,scepticism_threshold=.25,weight_method="linear"):
        super(ScepticalReputationBehavior, self).__init__()
        self.scepticism_threshold=scepticism_threshold
        self.weight_method=weight_method
        self.comparison_method=comparison_method
        self.scaling=scaling
        self.pending_information = {location: {} for location in Location}
        self.required_information=RequiredInformation.GLOBAL

    @staticmethod
    def difference_score(current_vector, bought_vector):
        v_norm = norm(current_vector)
        score = norm(current_vector - bought_vector) / v_norm if v_norm > 0.0 else 1000
        return score


    def step(self, api):
        super().step(api)
        self.update_pending_information()


    def update_pending_information(self):
        for location in Location:
            for target in self.pending_information[location].values():
                target.update(self.dr)
                target.rotate(-get_orientation_from_vector(self.dr))


    def get_reputation_score(self,payment_database:PaymentDB,bot_id):
        return payment_database.get_reward(bot_id)


    def get_skepticism_threshold(self,payment_database:PaymentDB,bot_id):
        reputation_score=self.get_reputation_score(payment_database,bot_id)
        # extension, metric=re.split("_",self.comparison_method)
        extension, metric=self.comparison_method[:-3],self.comparison_method[-3:]
        reputation_dict = {"all":{
                            "max":payment_database.get_highest_reward,
                            "avg":payment_database.get_average_reward,
                            "min":payment_database.get_lowest_reward,
                            },
                        }
        try:
            # return self.weighted_sceticism(reputation_score,reputation_dict[extension][metric])
            return self.weight_scepticism(reputation_score,reputation_dict[extension][metric]())
        except KeyError:
            return self.scepticism_threshold


    def weight_scepticism(self,reputation_score,metric_score):
        #TODO fix wrong initialization of behaviour, causing some to have default
        # print(self.weight_method)
        try:
            if self.weight_method=="linear":
                if reputation_score>metric_score:
                    threshold= self.scepticism_threshold-reputation_score/metric_score
                else:
                    threshold= self.scepticism_threshold+reputation_score/metric_score
                return max(0,threshold)
            elif self.weight_method=="ratio":
                return self.scepticism_threshold*reputation_score/metric_score
            elif self.weight_method=="exponential":
                return self.scepticism_threshold*(reputation_score/metric_score)**2
            elif self.weight_method=="logarithmic":
                return self.scepticism_threshold*np.log(reputation_score/metric_score)
        except:
            return self.scepticism_threshold


    def buy_info(self, payment_database:PaymentDB,session: CommunicationSession):
        for location in Location:
            metadata = session.get_metadata(location)
            metadata_sorted_by_age = sorted(metadata.items(), key=lambda item: item[1]["age"])
            for bot_id, data in metadata_sorted_by_age:
                if data["age"] < self.navigation_table.get_age_for_location(location) and bot_id not in \
                        self.pending_information[location]:
                    try:
                        other_target = session.make_transaction(neighbor_id=bot_id, location=location)
                        other_target.set_distance(other_target.get_distance() + session.get_distance_from(
                            bot_id))
                        if not self.navigation_table.is_information_valid_for_location(location) or \
                                self.difference_score(
                                    self.navigation_table.get_relative_position_for_location(location),
                                    other_target.get_distance())\
                                < self.get_skepticism_threshold(payment_database,bot_id):
                            new_target = self.strategy.combine(self.navigation_table.get_information_entry(location),
                                                               other_target,
                                                               np.array([0, 0]))
                            self.navigation_table.replace_information_entry(location, new_target)
                            self.pending_information[location].clear()
                        else:
                            for target in self.pending_information[location].values():
                                if self.difference_score(target.get_distance(),
                                                         other_target.get_distance()) \
                                        < self.get_skepticism_threshold(payment_database,bot_id):
                                    new_target = self.strategy.combine(target,
                                                                       other_target,
                                                                       np.array([0, 0]))
                                    self.navigation_table.replace_information_entry(location, new_target)
                                    self.pending_information[location].clear()
                                    break
                            else:
                                self.pending_information[location][bot_id] = other_target
                    except InsufficientFundsException:
                        pass
                    except NoInformationSoldException:
                        pass


