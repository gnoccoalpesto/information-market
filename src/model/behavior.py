import copy
import re
from abc import ABC, abstractmethod
from enum import Enum
from math import cos, radians, sin
import numpy as np

from model.payment import PaymentDB
from model.communication import CommunicationSession
from model.navigation import Location, NavigationTable
from model.strategy import WeightedAverageAgeStrategy, strategy_factory
from helpers.utils import get_orientation_from_vector, norm, InsufficientFundsException, NoInformationSoldException, \
    NoLocationSensedException


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

#TODO add, INFORMATION_ORDERING_METRICS, STRATEGY,...
# def required_information_for_behavior(behavior):
#     behaviors_list={
#         "NaiveBehavior": RequiredInformation.LOCAL,
#         "SaboteurBehavior": RequiredInformation.LOCAL,
#         "ScepticalBehavior": RequiredInformation.LOCAL,
#         "ScaboteurBehavior": RequiredInformation.LOCAL,
#         "ReputationWealthBehavior": RequiredInformation.GLOBAL,
#         "ReputationTresholdBehaviour": RequiredInformation.GLOBAL,
#         "ReputationStaticThresholdBehavior": RequiredInformation.GLOBAL,
#         "SaboteurReputationStaticThresholdBehavior": RequiredInformation.GLOBAL,
#         "ReputationDynamicThresholdBehavior": RequiredInformation.GLOBAL,
#         "SaboteurReputationDynamicThresholdBehavior": RequiredInformation.GLOBAL,
#         "ScepticalReputationBehavior": RequiredInformation.GLOBAL,
#         "SaboteurScepticalReputationBehavior": RequiredInformation.GLOBAL,
#         "WealthWeightedBehaviour": RequiredInformation.GLOBAL,
#         "SaboteurWealthWeightedBehaviour": RequiredInformation.GLOBAL,
#     }
#     return behaviors_list[behavior]

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


class TemplateBehaviour(Behavior):
    def __init__(self):
        super().__init__()
        # self.color = "blue"
        # self.navigation_table = NavigationTable()
        self.state = State.EXPLORING
        self.strategy = None
        self.dr = np.array([0, 0]).astype('float64')
        self.id = -1
        self.required_information = -1
        self.INFORMATION_ORDERING_METRICS=""

    def get_metadata(self,location: Location, payment_database: PaymentDB,session: CommunicationSession):
        metadata = session.get_metadata(location)
        # for bot_id in metadata:
        #     metadata[bot_id]["reputation"] = payment_database.get_reward(bot_id)
        return metadata


    def order_metadata(self, metadata):
        return sorted(metadata.items(), key=lambda item: 
                     item[1][self.INFORMATION_ORDERING_METRICS])


    def test_data_validity(self,location:Location,data,bot_id):
        """
        test if data is valid; could also have behaviour specific traits

        TODO: should i use should combine from strategy?
        """
        #return self.strategy.should_combine(data[self.INFORMATION_ORDERING_METRICS])
        # return data[self.INFORMATION_ORDERING_METRICS] < self.navigation_table.get_age_for_location(location)
        return True


    def transaction_and_referencing(self,location:Location,session: CommunicationSession,seller_id):
        other_target = session.make_transaction(neighbor_id=seller_id, location=location)
        other_target.set_distance(other_target.get_distance() + session.get_distance_from(seller_id))
        return other_target


    def test_data_quality(self,data):
        """
        test if data is convenient to buy in a behaviour and strategy specific way

        TODO: should i use should combine from strategy?
        """
        # return self.strategy.should_combine(data[self.INFORMATION_ORDERING_METRICS])
        return True

    
    def combine_data(self,location:Location, other_target,session: CommunicationSession,seller_id):
        """
        combine data with other target and update navigation table
        """
        new_target = self.strategy.combine(
            self.navigation_table.get_information_entry(location), 
            other_target,
            np.array([0, 0]))
        self.navigation_table.replace_information_entry(location, new_target)


    def stop_buying_process(self):
        """
        decision on continuing to buy information
        """
        return True

    def buy_info(self, payment_database:PaymentDB, session: CommunicationSession):
        for location in Location:
            metadata=self.get_metadata(location, payment_database, session)

            sorted_metadata=self.order_metadata(metadata)
            
            for bot_id, data in sorted_metadata:
                
                #TODO use self.strategy.should_combine(...)
                if self.test_data_validity(location,data,bot_id):
                    try:
                        other_target=self.transaction_and_referencing(location,session,bot_id)
                        
                        if self.test_data_quality(data):
                            self.combine_data(location, other_target,session,bot_id)

                        if self.stop_buying_process(): break

                    except (InsufficientFundsException, 
                            NoInformationSoldException, 
                            NoLocationSensedException): continue

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


#################################################################################################
## BASE BEHAVIORS
class NaiveBehavior(Behavior):
    def __init__(self):
        super().__init__()
        self.state = State.EXPLORING
        self.strategy = WeightedAverageAgeStrategy()
        self.dr = np.array([0, 0]).astype('float64')
        self.id = -1
        self.required_information = RequiredInformation.LOCAL


    def buy_info(self, session: CommunicationSession):
        for location in Location:
            metadata = session.get_metadata(location)
            metadata_sorted_by_age = sorted(metadata.items(), key=lambda item: item[1]["age"])
            for bot_id, data in metadata_sorted_by_age:
                if data["age"] < self.navigation_table.get_age_for_location(location):
                    try:
                        other_target = session.make_transaction(neighbor_id=bot_id, location=location)
                        new_target = self.strategy.combine(self.navigation_table.get_information_entry(location),
                                                           other_target,
                                                           session.get_distance_from(bot_id))
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


#####################################
# #
class CarefulBehavior(NaiveBehavior):
    def __init__(self, security_level=3):
        super(CarefulBehavior, self).__init__()
        self.color = "deep sky blue"
        self.security_level = security_level
        self.pending_information = {location: {} for location in Location}


    def buy_info(self, session: CommunicationSession):
        for location in Location:
            metadata = session.get_metadata(location)
            metadata_sorted_by_age = sorted(metadata.items(), key=lambda item: item[1]["age"])
            for bot_id, data in metadata_sorted_by_age:
                if data["age"] < self.navigation_table.get_age_for_location(location) and bot_id not in \
                        self.pending_information[
                            location]:
                    try:
                        other_target = session.make_transaction(neighbor_id=bot_id, location=location)
                        other_target.set_distance(other_target.get_distance() + session.get_distance_from(bot_id))
                        if not self.navigation_table.is_information_valid_for_location(location):
                            self.navigation_table.replace_information_entry(location, other_target)
                        else:
                            self.pending_information[location][bot_id] = other_target
                            if len(self.pending_information[location]) >= self.security_level:
                                self.combine_pending_information(location)
                    except InsufficientFundsException:
                        pass
                    except NoInformationSoldException:
                        pass


    def combine_pending_information(self, location):
        distances = [t.get_distance() for t in self.pending_information[location].values()]
        mean_distance = np.mean(distances, axis=0)
        best_target = min(self.pending_information[location].values(),
                          key=lambda t: norm(t.get_distance() - mean_distance))
        self.navigation_table.replace_information_entry(location, best_target)
        self.pending_information[location].clear()


    def step(self, api):
        super().step(api)
        self.update_pending_information()


    def update_pending_information(self):
        for location in Location:
            for target in self.pending_information[location].values():
                target.update(self.dr)
                target.rotate(-get_orientation_from_vector(self.dr))


    def debug_text(self):
        return f"size of pending: {[len(self.pending_information[l]) for l in Location]}\n" \
               f"{self.pending_information[Location.FOOD]}\n" \
               f"{self.pending_information[Location.NEST]}"


class SaboteurBehavior(NaiveBehavior):
    def __init__(self, rotation_angle=90):
        super().__init__()
        self.color = "red"
        self.rotation_angle = rotation_angle

    def sell_info(self, location):
        t = copy.deepcopy(self.navigation_table.get_information_entry(location))
        t.rotate(self.rotation_angle)
        return t


class GreedyBehavior(NaiveBehavior):
    def __init__(self):
        super().__init__()
        self.color = "green"

    def sell_info(self, location):
        t = copy.deepcopy(self.navigation_table.get_information_entry(location))
        t.age = 1
        return t


##################################################################################################
# # SKEPTICISM
class ScepticalBehavior(NaiveBehavior):
    def __init__(self, threshold=.25):
        super(ScepticalBehavior, self).__init__()
        self.pending_information = {location: {} for location in Location}
        self.threshold = threshold

    def buy_info(self, session: CommunicationSession):
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
                                < self.threshold:
                            new_target = self.strategy.combine(self.navigation_table.get_information_entry(location),
                                                               other_target,
                                                               np.array([0, 0]))
                            self.navigation_table.replace_information_entry(location, new_target)
                            self.pending_information[location].clear()
                        else:
                            for target in self.pending_information[location].values():
                                if self.difference_score(target.get_distance(),
                                                         other_target.get_distance()) \
                                        < self.threshold:
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

    @staticmethod
    def difference_score(current_vector, bought_vector):
        v_norm = norm(current_vector)
        score = norm(current_vector - bought_vector) / v_norm if v_norm > 0 else 1000
        return score

    def step(self, api):
        super().step(api)
        self.update_pending_information()

    def update_pending_information(self):
        for location in Location:
            for target in self.pending_information[location].values():
                target.update(self.dr)
                target.rotate(-get_orientation_from_vector(self.dr))


class FreeRiderBehavior(ScepticalBehavior):
    def __init__(self):
        super().__init__()
        self.color = "pink"

    def sell_info(self, location):
        return None


class ScaboteurBehavior(ScepticalBehavior):
    def __init__(self, rotation_angle=90, threshold=.25):
        super().__init__()
        self.color = "red"
        self.rotation_angle = rotation_angle
        self.threshold = threshold

    def sell_info(self, location):
        t = copy.deepcopy(self.navigation_table.get_information_entry(location))
        t.rotate(self.rotation_angle)
        return t


class ScepticalGreedyBehavior(ScepticalBehavior):
    def __init__(self):
        super().__init__()
        self.color = "green"

    def sell_info(self, location):
        t = copy.deepcopy(self.navigation_table.get_information_entry(location))
        t.age = 1
        return t


###################################################################################
# BEHAVIOURS WITH REPUTATION (SYSTEMIC) PROTECTION ################################

# class SimpleReputationBehaviour



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
                            # print("sold")####    ####     ####     #####
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
    # def get_treshold_value(self, session: CommunicationSession):
    def get_treshold_value(self):
        pass

    def verify_reputation(self,payment_database:PaymentDB, session: CommunicationSession, bot_id):
        # return self.get_reputation_score(session, bot_id) >\
        return self.get_reputation_score(payment_database, bot_id) >\
                 self.get_treshold_value(payment_database, session)


class ReputationStaticThresholdBehavior(ReputationTresholdBehaviour):
    def __init__(self,threshold=1):
        super(ReputationStaticThresholdBehavior, self).__init__()
        self.reputation_threshold=threshold

    def get_treshold_value(self, payment_database:PaymentDB,session: CommunicationSession):
            return self.reputation_threshold


class SaboteurReputationStaticThresholdBehavior(ReputationStaticThresholdBehavior):
    def __init__(self, threshold=1,rotation_angle=90):
        super().__init__()
        self.color = "red"
        self.rotation_angle = rotation_angle

    def sell_info(self, location):
        t = copy.deepcopy(self.navigation_table.get_information_entry(location))
        t.rotate(self.rotation_angle)
        return t


class ReputationDynamicThresholdBehavior(ReputationTresholdBehaviour):
    def __init__(self,method="all_max",scaling=1):
        super(ReputationDynamicThresholdBehavior, self).__init__()
        self.method=method
        self.scaling=scaling

    def get_treshold_value(self, payment_database:PaymentDB,session: CommunicationSession):
        """
        all_max: selects only above a certain percentage of maximum wealth (wealthiest bots), of all robots
        all_avg:selects only above certain percentage of average wealth, considering all robots
        all_min: selects only above a certain percentage of minimum wealth (poorest bots), of all robots
        TODO: all_rise:  selects above a certaint value, increasing with time, starting from a certain level, of all robots

        DEPRECATED:
        neigh_max: selects only above a certain percentage of maximum wealth (wealthiest bots), of neighbors
        neigh_avg: selects only above certain percentage of average wealth, considering neighbors
        neigh_min: selects only above a certain percentage of minimum wealth (poorest bots), of neighbors
        """
        # print("trying")####    ####     ####     #####
        extension, metric=re.split("_",self.method)
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



class SaboteurReputationDynamicThresholdBehavior(ReputationDynamicThresholdBehavior):
    def __init__(self, method="all_max",scaling=1,rotation_angle=90):
        super().__init__()
        self.color = "red"
        self.rotation_angle = rotation_angle

    def sell_info(self, location):
        t = copy.deepcopy(self.navigation_table.get_information_entry(location))
        t.rotate(self.rotation_angle)
        return t


#########################################################################################
# SKEPTICISM + REPUTATION WITH WEALTH BEHAVIOURS

class ScepticalReputationBehavior(NaiveBehavior):
    def __init__(self,method="all_avg",scaling=1,base_scepticism=.25,weight_method="linear"):
        super(ScepticalReputationBehavior, self).__init__()
        self.base_scepticism=base_scepticism
        self.weight_method=weight_method
        self.method=method
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
        extension, metric=re.split("_",self.method)

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
            return self.base_scepticism


    def weight_scepticism(self,reputation_score,metric_score):
        #TODO fix wrong initialization of behaviour, causing some to have default
        # print(self.weight_method)
        try:
            if self.weight_method=="linear":
                if reputation_score>metric_score:
                    threshold= self.base_scepticism-reputation_score/metric_score
                else:
                    threshold= self.base_scepticism+reputation_score/metric_score
                return max(0,threshold)
            elif self.weight_method=="ratio":
                return self.base_scepticism*reputation_score/metric_score
            elif self.weight_method=="exponential":
                return self.base_scepticism*(reputation_score/metric_score)**2
            elif self.weight_method=="logarithmic":
                return self.base_scepticism*np.log(reputation_score/metric_score)
        except:
            return self.base_scepticism


    def buy_info(self, session: CommunicationSession,payment_database:PaymentDB):
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


class SaboteurScepticalReputationBehavior(ScepticalReputationBehavior):
    def __init__(self,method="all_avg",scaling=1,base_scepticism=.25,weight_method="logarithmic", rotation_angle=90):
        super().__init__()
        self.color = "red"
        self.rotation_angle = rotation_angle

    def sell_info(self, location):
        t = copy.deepcopy(self.navigation_table.get_information_entry(location))
        t.rotate(self.rotation_angle)
        return t



class WealthWeightedBehaviour(NaiveBehavior):


    def __init__(self):
        super().__init__()
        self.required_information=RequiredInformation.GLOBAL


    def get_wealth_score(self,payment_database:PaymentDB,bot_id):
        return payment_database.get_reward(bot_id)


    def get_wealth_weight(self,payment_database:PaymentDB,bot_id):
        wealth_score=self.get_wealth_score(payment_database,bot_id)
        return wealth_score/payment_database.get_total_reward()


    def buy_info(self, session: CommunicationSession, payment_database:PaymentDB):
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
                                < self.get_wealth_weight(payment_database,bot_id):
                            new_target = self.strategy.combine(self.navigation_table.get_information_entry(location),
                                                               other_target,
                                                               np.array([0, 0]))
                            self.navigation_table.replace_information_entry(location, new_target)
                            self.pending_information[location].clear()
                        else:
                            for target in self.pending_information[location].values():
                                if self.difference_score(target.get_distance(),
                                                         other_target.get_distance()) \
                                        < self.get_wealth_weight(payment_database,bot_id):
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



######################################################
# BASED ON NEW TEMPLATE

class NewNaiveBehavior(TemplateBehaviour):
    def __init__(self):
        super().__init__()
        self.required_information=RequiredInformation.LOCAL
        self.INFORMATION_ORDERING_METRICS="age"
        self.strategy=strategy_factory("WeightedAverageAgeStrategy")

    def test_data_validity(self, location: Location, data,seller_id):
        return data[self.INFORMATION_ORDERING_METRICS] <\
             self.navigation_table.get_age_for_location(location)
        

class NewSaboteurBehavior(NewNaiveBehavior):
    def __init__(self,rotation_angle=90):
        super().__init__()
        self.color = "red"
        self.rotation_angle = rotation_angle

    def sell_info(self, location):
        t = copy.deepcopy(self.navigation_table.get_information_entry(location))
        t.rotate(self.rotation_angle)
        return t

class NewScepticalBehavior(NewNaiveBehavior):
    def __init__(self,base_scepticism=.25):
        super().__init__()
        self.scepticism_threshold=base_scepticism
        self.pending_information = {location: {} for location in Location}


    def test_data_validity(self, location: Location, data,seller_id):
        if data[self.INFORMATION_ORDERING_METRICS] <\
                self.navigation_table.get_age_for_location(location) \
                and seller_id not in self.pending_information[location]:
            return True
        return False

    def difference_score(self, target1, target2):
        return abs(target1 - target2)

    def test_data_quality(self,location:Location, other_target):
        if not self.navigation_table.is_information_valid_for_location(location)\
                or self.difference_score(
                    self.navigation_table.get_relative_position_for_location(location),
                    other_target.get_distance())\
                < self.scepticism_threshold:
            return True
        return False