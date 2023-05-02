import copy
from abc import ABC, abstractmethod
from enum import Enum
from math import cos, radians, sin
import numpy as np

from model.payment import PaymentDB
from model.communication import CommunicationSession
from model.navigation import Location, NavigationTable, Target
from model.strategy import WeightedAverageAgeStrategy, strategy_factory
from helpers.utils import get_orientation_from_vector, norm, InsufficientFundsException, \
    NoInformationSoldException, NoLocationSensedException
import config as CONFIG_FILE


BEHAVIORS_DICT = {  "n": "NaiveBeahvior",
                    "Nn": "NewNaiveBehavior",
                    "s": "ScepticalBehavior",
                    "Ns": "NewScepticalBehavior",
                    "r": "ReputationRankingBehavior",
                    "v": "VariableScepticalBehavior",
                    "Nv": "NewVariableScepticalBehavior",
                    "t": "WealthThresholdBehavior",
                    "w": "WealthWeightedBehavior",
                    "h": "ReputationHistoryBehavior",
                    }
BEHAVIORS_NAME_DICT = {  "n": "Naive",
                        "Nn": "Naive",
                        "s": "Sceptical",
                        "Ns": "Sceptical",
                        # "r": "Reputation Ranking",
                        "r": "Rep. Ranking",
                        # "v": "Variable Scepticism",
                        # "Nv": "Variable Scepticism",
                        "v": "Variable Sc.",
                        "Nv": "Variable Sc.",
                        "t": "Rep. Threshold",
                        "w": "Rep. Weighted",
                        # "t": "Reputation Threshold",
                        # "w": "Reputation Weighted",
                        "h": "Rep. History",
                    }
SUB_FOLDERS_DICT={  "n": "naive",
                    "Nn": "new_naive",
                    "s": "sceptical",
                    "Ns": "new_sceptical",
                    "r": "ranking",
                    "v": "variable_scepticism",
                    "Nv": "variable_scepticism",
                    "t": "wealth_threshold",
                    "w": "wealth_weighted",
                    "h": "history",
                    }
PARAMS_NAME_DICT={
                    "ST": "scepticism threshold",
                    "RT": "ranking threshold",
                    "CM": "comparison method",
                    "SC": "scaling",
                    "WM": "weight method",
                    "CS": "combine strategy",
                    "P": "penalization",
                    "NP": "non penalization",
                    "LIA": "lie angle",
                    "SMU": "bimodal noise sampling mean",
                    "SSD": "bimodal noise sampling stdev",
                    "NSD": "bimodal noise stdev",
                    "NMU": "uniform noise mean",
                    "NRANG": "uniform noise range",
                    "SAB": "saboteur performance",
                    "VM": "verification method",
                    "TM": "threshold method",
                    }
BEHAVIOR_PARAMS_DICT = {"n": [],
                        "Nn": [],
                        "s": ["ST"],
                        "Ns": ["ST"],
                        "r": ["RT"],
                        "v": ["CM","SC","ST","WM"],
                        "Nv": ["CM","SC","ST","WM"],
                        "t": ["CM","SC"],
                        "w": [],
                        "h": ["VM","TM"],
                        }
COMBINE_STRATEGY_DICT = {
                            "waa" : "WeightedAverageAgeStrategy",
                            "wara" : "WeightedAverageReputationAgeStrategy",
                            "rwar" : "RunningWeightedAverageReputationStrategy",
                            "nrwar" : "NewRunningWeightedAverageReputationStrategy",
                            "fwar" : "FullWeightedAverageReputationStrategy",
                            "nfwar" : "NewFullWeightedAverageReputationStrategy",
                            }
COMBINE_STRATEGY_NAME_DICT = {
                            "waa" : "Weighted Average Age",
                            "wara" : "Weighted Average Reputation Age",
                            "rwar" : "Running Weighted Average Reputation",
                            "nrwar" : "New Running Weighted Average Reputation",
                            "fwar" : "Full Weighted Average Reputation",
                            "nfwar" : "New Full Weighted Average Reputation",
                            }
NOISE_PARAMS_DICT={ "bimodal": ["SMU","SSD","NSD"],
                    "uniform": ["NMU","NRANG","SAB"],
                }
BEST_PARAM_COMBINATIONS_DICT={
                            "n": [
                                ['NP',[]],
                                # ['P',[]],
                                ],
                            # "Nn": [['NP',[]],['P',[]],],
                            "s": [
                                # ['NP',['025']],
                                ['P',['025']],],
                            # "Ns": [['NP',['025']],['P',['025']],],
                            "r": [
                                ['P', ['03']],
                                ],
                            "v": [],
                            "Nv": [
                                ['P', ['allavg', '03', '025', 'exponential']],
                                ['P', ['allavg', '03', '025', 'ratio']],
                                ],
                            "t": [
                                # ['P', ['allavg', '03']],
                                ['P', ['allavg', '05']],
                                ],
                            "w": [],
                            "h": [
                                ['P', ['discrete', 'mean']],
                                ['P', ['aged', 'mean']],
                                ],
                            }

BAD_PARAM_COMBINATIONS_DICT={
                    #TODO could use dots in filenames
                    "n": [],
                    "Nn": [],
                    "s": [],
                    "Ns": [],
                    "r": [
                        ['NP', ['03']],
                        ['NP', ['05']],
                        ],
                    "v": [],
                    "Nv": [
                        ['NP', ['allavg', '03', '025', 'exponential']],
                        ['NP', ['allavg', '03', '025', 'ratio']],
                        ['NP', ['allavg', '05', '025', 'exponential']],
                        ['NP', ['allavg', '08', '025', 'exponential']],
                        ['NP', ['allmax', '03', '025', 'exponential']],
                        ['NP', ['allmax', '08', '025', 'exponential']],
                        ['NP', ['allmax', '08', '025', 'exponential']],
                        ['P', ['allavg', '08', '025', 'exponential']],
                        ['P', ['allavg', '08', '025', 'ratio']],
                        ['P', ['allmax', '03', '025', 'exponential']],
                        ['P', ['allmax', '03', '025', 'ratio']],
                        ['P', ['allmax', '05', '025', 'exponential']],
                        ['P', ['allmax', '05', '025', 'ratio']],
                        ['P', ['allmax', '08', '025', 'exponential']],
                        ['P', ['allmax', '08', '025', 'ratio']],
                        ],
                    "t": [
                        ['NP', ['allavg', '03']],
                        ['NP', ['allavg', '05']],
                        ['NP', ['allavg', '08']],
                        ['NP', ['allmax', '03']],
                        ['NP', ['allmax', '05']],
                        ['NP', ['allmax', '08']],
                        ['P', ['allmax', '05']],
                        ['P', ['allmax', '08']],
                        ],
                    "w": [],
                    "w": [
                        ['NP',[]],
                        ['P',[]],
                    ],
                    "h": [
                        ['P', ['discrete', 'positive']],
                        ['P', ['difference', 'positive']],
                        ['P', ['recency', 'positive']],
                        ['P', ['aged', 'positive']],
                        ['P', ['aged2', 'positive']],
                        ['NP', ['discrete', 'positive']],
                        ['NP', ['difference', 'positive']],
                        ['NP', ['recency', 'positive']],
                        ['NP', ['aged', 'positive']],
                        ['NP', ['aged2', 'positive']],
                        ['P', ['recency', 'mean']],
                        ['P', ['aged2', 'mean']],
                        ['NP', ['discrete', 'mean']],
                        ['NP', ['difference', 'mean']],
                        ['NP', ['recency', 'mean']],
                        ['NP', ['aged', 'mean']],
                        ['NP', ['aged2', 'mean']],
                    ],
                }


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
#         "VariableScepticalBehavior": RequiredInformation.GLOBAL,
#         "SaboteurVariableScepticalBehavior": RequiredInformation.GLOBAL,
#         "WealthWeightedBehavior": RequiredInformation.GLOBAL,
#         "SaboteurWealthWeightedBehavior": RequiredInformation.GLOBAL,
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
    def __init__(self,combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__()
        self.state = State.EXPLORING
        self.strategy = strategy_factory(combine_strategy)
        self.dr = np.array([0, 0]).astype('float64')
        self.id = -1
        self.required_information = -1
        self.information_ordering_metric=""


    def buy_info(self, payment_database:PaymentDB, session: CommunicationSession):
        #TODO if self.start_buying():
            for location in Location:
                sorted_metadata=self.get_ordered_metadata(location, payment_database, session)

                for seller_id, data in sorted_metadata:
                    session.record_transaction('attempted',seller_id)

                    if self.test_data_validity(location,data,payment_database,seller_id):
                        session.record_transaction('validated',seller_id)

                        try:
                            target=self.navigation_table.get_information_entry(location)
                            other_target=self.acquire_referenced_info(location,session,seller_id)

                            if self.test_data_quality(location,other_target,payment_database,seller_id):
                                session.record_transaction('combined',seller_id)

                                self.combine_data(location,target, other_target,payment_database,seller_id)

                            else:
                                self.behavior_specific_combine(location, other_target,session,seller_id)

                            if self.stop_buying(): break

                        except (InsufficientFundsException,
                                NoInformationSoldException,
                                NoLocationSensedException): continue


    def get_ordered_metadata(self,location: Location, payment_database: PaymentDB,session: CommunicationSession):
        #TODO reward ordering bypassed
        metadata = session.get_metadata(location)
        # if self.information_ordering_metric == "reputation":
        #     for bot_id in metadata:
        #         metadata[bot_id]["reputation"] = payment_database.get_reward(bot_id)
        sorted_metadata= sorted(metadata.items(), key=lambda item:
                     item[1]["age"])
                    #  item[1][self.information_ordering_metric])
        # return reversed(sorted_metadata) if self.information_ordering_metric == "reputation" \
        #         else sorted_metadata
        return sorted_metadata


    def start_buying(self):
        return True
    

    def test_data_validity(self,location:Location,data,payment_database,bot_id):
        """
        test if data is valid to be bought; could also have behaviour specific traits
        TODO return self.strategy.should_combine(data[self.information_ordering_metric])"""
        return True


    def acquire_referenced_info(self,location:Location,session: CommunicationSession,seller_id):
        """
        buys information and references it into local ref. frame
        """
        other_target = session.make_transaction(neighbor_id=seller_id, location=location)
        other_target.set_distance(other_target.get_distance() + session.get_distance_from(seller_id))
        return other_target


    def test_data_quality(self,location:Location,other_target:Target,payment_database:PaymentDB,seller_id):
        """
        tests if data is good enough to be combined with local data; behaviour and strategy specific
        # return data[self.information_ordering_metric] < self.navigation_table.get_age_for_location(location)
        """
        return True


    def combine_data(self,location:Location,target:Target, other_target:Target,
                                payment_database:PaymentDB, seller_id):
        """
        combine data with other target and update navigation table

        TODO more elegantly pass kwargs using a dict
        """
        if self.strategy.__class__.__name__ == "WeightedAverageAgeStrategy":
            new_target = self.strategy.combine(
                        target,
                        other_target,
                        np.array([0, 0]))

        elif self.strategy.__class__.__name__ == "WeightedAverageReputationAgeStrategy":
            mean_reputation = payment_database.get_mean_reward()
            seller_reputation = payment_database.get_reward(seller_id)
            new_target=self.strategy.combine(
                        target,
                        other_target,
                        np.array([0, 0]),
                        mean_reputation,
                        seller_reputation)

        elif self.strategy.__class__.__name__ == "NewRunningWeightedAverageReputationStrategy":
            mean_reputation = payment_database.get_mean_reward()
            seller_reputation = payment_database.get_reward(seller_id)
            new_target=self.strategy.combine(
                        target,
                        other_target,
                        mean_reputation,
                        seller_reputation)

        elif self.strategy.__class__.__name__ == "FullWeightedAverageReputationStrategy":
            new_target=self.strategy.combine(
                        target,
                        other_target,
                        self.id,
                        seller_id,
                        payment_database
                        )

        elif self.strategy.__class__.__name__ == "NewFullWeightedAverageReputationStrategy":
            new_target=self.strategy.combine(
                        target,
                        other_target,
                        seller_id,
                        payment_database
                        )

        elif self.strategy.__class__.__name__ == "RunningWeightedAverageReputationStrategy":
            my_reputation = payment_database.get_reward(self.id)
            seller_reputation = payment_database.get_reward(seller_id)
            new_target=self.strategy.combine(
                        target,
                        other_target,
                        my_reputation,
                        seller_reputation)
                        
        self.navigation_table.replace_information_entry(location, new_target)


    # @abstractmethod
    def behavior_specific_combine(self,location:Location, other_target:Target,session: CommunicationSession,seller_id):
        """
        combine data with other target and update navigation table
        """
        pass


    def stop_buying(self):
        """
        decision on continuing to buy information
        """
        return True


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
#################################################################################################
#################################################################################################
## NAIVE BEHAVIORS
class NaiveBehavior(Behavior):
    def __init__(self,combine_strategy="WeightedAverageAgeStrategy"):
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
                session.record_transaction('attempted',bot_id)

                if data["age"] < self.navigation_table.get_age_for_location(location):
                    session.record_transaction('validated',bot_id)
                    try:
                        other_target = session.make_transaction(neighbor_id=bot_id, location=location)
                        new_target = self.strategy.combine(self.navigation_table.get_information_entry(location),
                                                           other_target,
                                                           session.get_distance_from(bot_id))
                        session.record_transaction('combined',bot_id)
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


class SaboteurBehavior(NaiveBehavior):
    def __init__(self, lie_angle=90,combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__()
        self.color = "red"
        self.lie_angle = lie_angle

    def sell_info(self, location):
        t = copy.deepcopy(self.navigation_table.get_information_entry(location))
        t.rotate(self.lie_angle)
        return t


##################################################################################################
# # SKEPTICISM
class ScepticalBehavior(NaiveBehavior):
    def __init__(self, threshold=.25,combine_strategy="WeightedAverageAgeStrategy"):
        super(ScepticalBehavior, self).__init__()
        self.pending_information = {location: {} for location in Location}
        self.threshold = threshold


    def buy_info(self, _,session: CommunicationSession):
        for location in Location:
            metadata = session.get_metadata(location)
            metadata_sorted_by_age = sorted(metadata.items(), key=lambda item: item[1]["age"])
            for bot_id, data in metadata_sorted_by_age:
                session.record_transaction('attempted', bot_id)

                if data["age"] < self.navigation_table.get_age_for_location(location) and bot_id not in \
                        self.pending_information[location]:
                    session.record_transaction('validated', bot_id)

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
                            session.record_transaction('combined', bot_id)
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
                                    session.record_transaction('combined', bot_id)
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


class ScaboteurBehavior(ScepticalBehavior):
    def __init__(self, lie_angle=90, threshold=.25,combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__()
        self.color = "red"
        self.lie_angle = lie_angle
        self.threshold = threshold

    def sell_info(self, location):
        t = copy.deepcopy(self.navigation_table.get_information_entry(location))
        t.rotate(self.lie_angle)
        return t


##################################################################################################
##################################################################################################
# # NEW CLASSICAL BEHAVIOURS
class NewNaiveBehavior(TemplateBehaviour):
    def __init__(self,combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(combine_strategy=combine_strategy)
        self.required_information=RequiredInformation.LOCAL
        self.information_ordering_metric="age"

    def test_data_validity(self, location: Location, data,_,__):
        return data[self.information_ordering_metric] <\
             self.navigation_table.get_age_for_location(location)


class NewSaboteurBehavior(NewNaiveBehavior):
    def __init__(self,lie_angle=90,combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(combine_strategy=combine_strategy)
        self.color = "red"
        self.lie_angle = lie_angle

    def sell_info(self, location):
        t = copy.deepcopy(self.navigation_table.get_information_entry(location))
        t.rotate(self.lie_angle)
        return t


class NewScepticalBehavior(TemplateBehaviour):
    def __init__(self,scepticism_threshold=.25,combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(combine_strategy=combine_strategy)
        self.required_information=RequiredInformation.LOCAL
        self.information_ordering_metric="age"
        self.pending_information = {location: {} for location in Location}
        self.scepticism_threshold=scepticism_threshold

    def get_scepticism_threshold(self,_,__):
        return self.scepticism_threshold

    def test_data_validity(self, location: Location, data,_,seller_id):
        if data[self.information_ordering_metric] <\
                self.navigation_table.get_age_for_location(location) \
                and seller_id not in self.pending_information[location]:
            return True
        return False


    @staticmethod
    def difference_score(current_vector, bought_vector):
        v_norm = norm(current_vector)
        score = norm(current_vector - bought_vector) / v_norm if v_norm > 0 else 1000
        return score
    #TODO test which is better: def difference_score(self,location,other_target:Target):
    #     current_vector=self.navigation_table.get_relative_position_for_location(location)
    #     bought_vector=other_target.get_distance()
    #     v_norm = norm(current_vector)
    #     score = norm(current_vector - bought_vector) / v_norm if v_norm > 0 else 1000
    #     return score


    def test_data_quality(self,location:Location, other_target,payment_database,seller_id):
        if not self.navigation_table.is_information_valid_for_location(location)\
                or self.difference_score(
                    self.navigation_table.get_relative_position_for_location(location),
                    other_target.get_distance())\
            < self.get_scepticism_threshold(payment_database, seller_id):
            return True
        return False


    def combine_data(self, location: Location,target:Target, other_target: Target, session: CommunicationSession, seller_id):
        super().combine_data(location,target, other_target, session, seller_id)
        self.pending_information[location].clear()


    def behavior_specific_combine(self, location: Location, other_target: Target, session: CommunicationSession, seller_id):
        for target in self.pending_information[location].values():
            if self.difference_score(target.get_distance(),
                                        other_target.get_distance()) \
                    < self.threshold:
                self.combine_data(location,target, other_target, session, seller_id)
                break
            else:
                self.pending_information[location][seller_id] = other_target


    def update_pending_information(self):
        for location in Location:
            for target in self.pending_information[location].values():
                target.update(self.dr)
                target.rotate(-get_orientation_from_vector(self.dr))


    def step(self, api):
        super().step(api)
        self.update_pending_information()


    def stop_buying(self):
        return False


class NewScaboteurBehavior(NewScepticalBehavior):
    def __init__(self,lie_angle=90,scepticism_threshold=.25,combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(combine_strategy=combine_strategy, 
                        scepticism_threshold=scepticism_threshold)
        self.color = "red"
        self.lie_angle = lie_angle

    def sell_info(self, location):
        t = copy.deepcopy(self.navigation_table.get_information_entry(location))
        t.rotate(self.lie_angle)
        return t


##################################################################################################
##################################################################################################
##################################################################################################
# BEHAVIOURS WITH REPUTATION (SYSTEMIC PROTECTION)

class WealthWeightedBehavior(TemplateBehaviour):
    def __init__(self,combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(combine_strategy=combine_strategy)
        self.required_information=RequiredInformation.GLOBAL
        self.information_ordering_metric="reputation"
        if self.strategy.__class__.__name__=="FullWeightedAverageReputationStrategy":
            self.bought_information = {location: {} for location in Location}


    def test_data_validity(self, location: Location, data,payment_database,seller_id):
        #TODO test data reputation usefull?...
        # average_reward=payment_database.get_average_reward()
        # return data[self.information_ordering_metric] >= SCALE*average_reward
        return data["age"] < self.navigation_table.get_age_for_location(location)


class SaboteurWealthWeightedBehavior(WealthWeightedBehavior):
    def __init__(self,lie_angle=90,combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(combine_strategy=combine_strategy)
        self.color = "red"
        self.lie_angle = lie_angle

    def sell_info(self, location):
        t = copy.deepcopy(self.navigation_table.get_information_entry(location))
        t.rotate(self.lie_angle)
        return t
    #############

class ReputationRankingBehavior(TemplateBehaviour):
    def __init__(self,ranking_threshold=.5,combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(combine_strategy=combine_strategy)
        self.required_information=RequiredInformation.GLOBAL
        self.information_ordering_metric="age"
        self.ranking_threshold=ranking_threshold
    

    def test_data_validity(self, location: Location, data,_,__):
        return data["age"] < self.navigation_table.get_age_for_location(location)


    def test_data_quality(self, location: Location, _, payment_database:PaymentDB, seller_id):
        if not self.navigation_table.is_information_valid_for_location(location)\
                or self.verify_reputation(payment_database, seller_id):
            return True
        return False


    def verify_reputation(self,payment_database:PaymentDB,seller_id):
        rank=payment_database.get_reputation_ranking(seller_id,"r")#'h'
        if rank is None:
            return True
        percentile=1-rank/payment_database.get_number_of_wallets()
        return percentile >= self.ranking_threshold
    

    def stop_buying(self):
        return False


class SaboteurReputationRankingBehavior(ReputationRankingBehavior):
    def __init__(self,lie_angle=90,ranking_threshold=.5,combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(ranking_threshold=ranking_threshold,
                        combine_strategy=combine_strategy)
        self.color = "red"
        self.lie_angle = lie_angle

    def sell_info(self, location):
        t = copy.deepcopy(self.navigation_table.get_information_entry(location))
        t.rotate(self.lie_angle)
        return t


class WealthThresholdBehavior(TemplateBehaviour):
    def __init__(self,comparison_method="allavg",scaling=.3,combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(combine_strategy=combine_strategy)
        self.required_information=RequiredInformation.GLOBAL
        self.information_ordering_metric="age"
        self.scaling=scaling
        self.comparison_method=comparison_method


    def test_data_validity(self, location: Location, data,_,__):
        return data["age"] < self.navigation_table.get_age_for_location(location)


    def test_data_quality(self, location: Location, _, payment_database:PaymentDB, seller_id):
        if not self.navigation_table.is_information_valid_for_location(location)\
                or self.verify_reputation(payment_database, seller_id):
            return True
        return False


    def stop_buying(self):
        return False


    def verify_reputation(self,payment_database:PaymentDB,seller_id):
        seller_reputation=payment_database.get_reputation(seller_id,"r")
        threshld_reputation=self.get_threshold_value(payment_database)
        return seller_reputation >= threshld_reputation if threshld_reputation is not None \
                                    and seller_reputation is not None  else False


    def get_threshold_value(self,payment_database:PaymentDB):
        """
        allmax: selects only above a certain percentage of maximum wealth (wealthiest bots), of all robots
        allavg:selects only above certain percentage of average wealth, considering all robots
        allmin: selects only above a certain percentage of minimum wealth (poorest bots), of all robots
        TODO: all_rise:  selects above a certaint value, increasing with time, starting from a certain level, of all robots

        NOTE DEPRECATED:
        neighmax: selects only above a certain percentage of maximum wealth (wealthiest bots), of neighbors
        neighavg: selects only above certain percentage of average wealth, considering neighbors
        neighmin: selects only above a certain percentage of minimum wealth (poorest bots), of neighbors
        """
        # extension, metric=re.split("_",self.comparison_method)
        extension, metric=self.comparison_method[:-3],self.comparison_method[-3:]
        reputation_dict = {"all":{
                                "max":payment_database.get_highest_reputation,
                                 "avg":payment_database.get_mean_reputation,
                                 "min":payment_database.get_lowest_reputation,
                                 },
                            # "neigh":{"COMPARISON_x": session.get_X_COMPARE,}
                            }
        reputation=reputation_dict[extension][metric]("r")
        return self.scaling*reputation if reputation is not None else None


class SaboteurWealthThresholdBehavior(WealthThresholdBehavior):
    def __init__(self,lie_angle=90,comparison_method="allavg",scaling=.3,combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(comparison_method=comparison_method,
                        scaling=scaling,
                        combine_strategy=combine_strategy)
        self.color = "red"
        self.lie_angle = lie_angle

    def sell_info(self, location):
        t = copy.deepcopy(self.navigation_table.get_information_entry(location))
        t.rotate(self.lie_angle)
        return t

#[ ]
class ReputationHistoryBehavior(TemplateBehaviour):
    def __init__(self,combine_strategy="WeightedAverageAgeStrategy",
                     verification_method="discrete",threshold_method='positive'):
        super().__init__(combine_strategy=combine_strategy)
        self.required_information=RequiredInformation.GLOBAL
        self.information_ordering_metric="age"
        self.verification_method=verification_method
        self.threshold_method=threshold_method


    def test_data_validity(self, location: Location, data,_,__):
        return data["age"] < self.navigation_table.get_age_for_location(location)


    def test_data_quality(self, location: Location, _, payment_database:PaymentDB, seller_id):
        if not self.navigation_table.is_information_valid_for_location(location)\
                or self.verify_reputation(payment_database, seller_id):
            return True
        return False


    def stop_buying(self):
        return False


        #[ ]
    def verify_reputation(self,payment_database:PaymentDB,seller_id):
        valid_history=[h for h in payment_database.get_history(seller_id) 
                        if h is not None]
        if len(valid_history)>0:
            reputation=0
            for i,h in enumerate(valid_history):
                #[ ]
                #TODO this should behave as a derivative controller, since
                # reputation can be ocnsidered as a discrete derivative of income
                Kd=CONFIG_FILE.KD_HISTORY_CONTROLLER
                if self.verification_method=="discrete":
                    increment=np.sign(h)
                elif self.verification_method=="difference":
                    increment=h
                elif self.verification_method=="recency":
                    increment=h*(i+1)
                elif self.verification_method=="aged":
                    increment=h/(len(valid_history)-i)
                elif self.verification_method=="aged2":
                    increment=h/(len(valid_history)-i)**2
                reputation+=Kd*increment

            return reputation>=CONFIG_FILE.SCALING_HISTORY_THRESHOLD*\
                                self.get_threshold_value(payment_database)
        return True


    def get_threshold_value(self,payment_database:PaymentDB):
        if self.threshold_method=='positive':
            return 0
        elif self.threshold_method=='mean':
            return payment_database.get_mean_reputation("h",self.verification_method)


class SaboteurReputationHistoryBehavior(ReputationHistoryBehavior):
    def __init__(self,lie_angle=90,combine_strategy="WeightedAverageAgeStrategy",
                    verification_method="discrete",threshold_method='positive'):
        super().__init__(verification_method=verification_method,
                        threshold_method=threshold_method,
                        combine_strategy=combine_strategy)
        self.color = "red"
        self.lie_angle = lie_angle


    def sell_info(self, location):
        t = copy.deepcopy(self.navigation_table.get_information_entry(location))
        t.rotate(self.lie_angle)
        return t


class NewVariableScepticalBehavior(NewScepticalBehavior):
    def __init__(self,scepticism_threshold=.25,comparison_method="allavg",
                    scaling=.3,weight_method="ratio",combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(scepticism_threshold=scepticism_threshold,
                        combine_strategy=combine_strategy)
        self.required_information=RequiredInformation.GLOBAL
        self.information_ordering_metric="age"
        self.scaling=scaling
        self.comparison_method=comparison_method
        self.weight_method=weight_method

    #[ ]
    def get_scepticism_threshold(self,payment_database:PaymentDB,seller_id):
        # reputation_score=payment_database.get_reward(seller_id)
        seller_reputation=payment_database.get_reputation(seller_id,"r")
        # extension, metric=re.split("_",self.comparison_method) #TODO could substitute with "-"
        extension, metric=self.comparison_method[:-3],self.comparison_method[-3:]

        reputation_dict = {"all":{
                                "max":payment_database.get_highest_reputation,
                                "avg":payment_database.get_mean_reputation,
                                "min":payment_database.get_lowest_reputation,
                            },
                        }
        comparison_reputation=reputation_dict[extension][metric]("r")
        return self.weight_scepticism(seller_reputation,comparison_reputation)


    def weight_scepticism(self,reputation_score,metric_score):
        try:
            if self.weight_method=="ratio":
                return self.scepticism_threshold*reputation_score/(metric_score*self.scaling)
            # elif self.weight_method=="linear":
            #     if reputation_score>metric_score:
            #         threshold= self.scepticism_threshold+reputation_score/metric_score
            #     else:
            #         threshold= self.scepticism_threshold-reputation_score/metric_score
            #     return max(0,threshold)
            elif self.weight_method=="exponential":
                return self.scepticism_threshold*(reputation_score/(metric_score*self.scaling))**2
            # elif self.weight_method=="logarithmic":
            #     return self.scepticism_threshold*np.log(reputation_score/(metric_score*self.scaling))
        except:
            return self.scepticism_threshold


class NewSaboteurVariableScepticalBehavior(NewVariableScepticalBehavior):
    def __init__(self,scepticism_threshold=.25,comparison_method="allavg",
                    scaling=.3,weight_method="ratio",lie_angle=90,combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(scepticism_threshold=scepticism_threshold,
                        comparison_method=comparison_method,
                        scaling=scaling,
                        weight_method=weight_method,
                        combine_strategy=combine_strategy)
        self.color = "red"
        self.lie_angle = lie_angle

    def sell_info(self, location):
        t = copy.deepcopy(self.navigation_table.get_information_entry(location))
        t.rotate(self.lie_angle)
        return t



############################################################################################################
############################################################################################################
############################################################################################################
# NEWCOMERS
class NewcomerNaiveBehavior (NaiveBehavior):
    def __init__(self, combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(combine_strategy)
        self.color = "green"

class NewcomerSaboteurBehavior (SaboteurBehavior):
    def __init__(self, lie_angle=90, combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(lie_angle, combine_strategy)
        self.color = "orange"

class NewcomerScepticalBehavior (ScepticalBehavior):
    def __init__(self, scepticism_threshold=.25, combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(scepticism_threshold, combine_strategy)
        self.color = "green"

class NewcomerScaboteurBehavior (ScaboteurBehavior):
    def __init__(self, lie_angle=90, scepticism_threshold=.25, combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(lie_angle, scepticism_threshold, combine_strategy)
        self.color = "orange"

class NewcomerReputationHistoryBehavior (ReputationHistoryBehavior):
    def __init__(self,verification_method="discrete",threshold_method='positive',
                    combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(verification_method=verification_method,
                        threshold_method=threshold_method,
                        combine_strategy=combine_strategy)
        self.color = "green"

class NewcomerSaboteurReputationHistoryBehavior (SaboteurReputationHistoryBehavior):
    def __init__(self,lie_angle=90,verification_method="discrete",threshold_method='positive',
                    combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(lie_angle=lie_angle,
                        verification_method=verification_method,
                        threshold_method=threshold_method,
                        combine_strategy=combine_strategy)
        self.color = "orange"
#TODO check if "New" in this name position causes problems
class NewcomerNewVariableScepticalBehavior (NewVariableScepticalBehavior):
    def __init__(self,scepticism_threshold=.25,comparison_method="allavg",
                    scaling=.3,weight_method="ratio",combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(scepticism_threshold=scepticism_threshold,
                        comparison_method=comparison_method,
                        scaling=scaling,
                        weight_method=weight_method,
                        combine_strategy=combine_strategy)
        self.color = "green"

class NewcomerNewSaboteurVariableScepticalBehavior (NewSaboteurVariableScepticalBehavior):
    def __init__(self,scepticism_threshold=.25,comparison_method="allavg",
                    scaling=.3,weight_method="ratio",lie_angle=90,combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(scepticism_threshold=scepticism_threshold,
                        comparison_method=comparison_method,
                        scaling=scaling,
                        weight_method=weight_method,
                        lie_angle=lie_angle,
                        combine_strategy=combine_strategy)
        self.color = "orange"

class NewcomerReputationRankingBehavior(ReputationRankingBehavior):
    def __init__(self,ranking_threshold=.5,
                    combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(ranking_threshold=ranking_threshold,
                        combine_strategy=combine_strategy)
        self.color = "green"

class NewcomerSaboteurReputationRankingBehavior(SaboteurReputationRankingBehavior):
    def __init__(self,lie_angle=90,ranking_threshold=.5,
                    combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(lie_angle=lie_angle,
                        ranking_threshold=ranking_threshold,
                        combine_strategy=combine_strategy)
        self.color = "orange"

class NewcomerWealthThresholdBehavior(WealthThresholdBehavior):
    def __init__(self,comparison_method="allavg",scaling=.3,combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(comparison_method=comparison_method,scaling=scaling,combine_strategy=combine_strategy)
        self.color = "green"

class NewcomerSaboteurWealthThresholdBehavior(SaboteurWealthThresholdBehavior):
    def __init__(self,lie_angle=90,comparison_method="allavg",scaling=.3,combine_strategy="WeightedAverageAgeStrategy"):
        super().__init__(lie_angle=lie_angle,comparison_method=comparison_method,scaling=scaling,combine_strategy=combine_strategy)
        self.color = "orange"

