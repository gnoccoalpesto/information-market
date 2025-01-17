import copy
import numpy as np

from random import random, choices, gauss
from math import sin, cos, radians
from collections import deque

from helpers import random_walk as rw
from model.behavior import State, behavior_factory, RequiredInformation, TemplateBehaviour
from model.communication import CommunicationSession
from model.navigation import Location
from helpers.utils import get_orientation_from_vector, rotate, InsufficientFundsException, CommunicationState, norm, \
    NoLocationSensedException
from model.payment import Transaction

class AgentAPI:
    def __init__(self, agent):
        self.speed = agent.speed
        self.get_sensors = agent.get_sensors
        self.set_desired_movement = agent.set_desired_movement
        self.get_id = agent.get_id
        self.carries_food = agent.carries_food
        self.radius = agent.radius
        self.get_relative_position_to_location = agent.get_relative_position_to_location
        self.get_levi_turn_angle = agent.get_levi_turn_angle


class Agent:
    '''
    NOTE: random numbers are discarded in case of non bimodal noise drawing to preserve the same sequence
    of the bimodal case, for spawn and following requests
    '''
    colors = {State.EXPLORING: "gray35", State.SEEKING_FOOD: "orange", State.SEEKING_NEST: "green"}

    def __init__(self,
                 robot_id,
                 x,
                 y,
                 environment,
                 behavior_params,
                 speed,
                 radius,
                 noise,
                 fuel_cost,
                 communication_radius,
                 communication_cooldown,
                 communication_stop_time
                 ):
        self.id = robot_id
        self.pos = np.array([x, y]).astype('float64')

        self._speed = speed
        self._radius = radius
        self.items_collected = 0
        self._carries_food = False
        # self._expiration_timer=0#[x]IEFM

        self.communication_radius = communication_radius
        self._communication_cooldown = communication_cooldown
        self._comm_stop_time = communication_stop_time
        self._time_since_last_comm = self._comm_stop_time + self._communication_cooldown + 1
        self.comm_state = CommunicationState.OPEN

        self.environment = environment
        #TODO move this in env, CHECK if correct rand sequence for same spawn
        self.orientation = random() * 360

        if noise["class"] == "BimodalNoise":
            self.bimodal_noise = True
            noise_sampling_mu = noise["parameters"]["noise_sampling_mu"]
            noise_sampling_sigma = noise["parameters"]["noise_sampling_sigma"]
            self.noise_mu = gauss(noise_sampling_mu, noise_sampling_sigma)
            if random() >= 0.5:
                self.noise_mu = -self.noise_mu
            self.noise_sd = noise["parameters"]["noise_sd"]
        else:
            gauss(0,0);random()#discard r.n. from the sequence
            self.bimodal_noise=False
            self.noise_mu = noise["parameters"]["noise_mu"]

        self.fuel_cost = fuel_cost

        self.levi_counter = 1
        self.trace = deque(self.pos, maxlen=100)

        self.dr = np.array([0, 0])
        self.sensors = {}
        self.behavior:TemplateBehaviour = behavior_factory(behavior_params)
        self.api = AgentAPI(self)


    def __str__(self):
        return f"ID: {self.id}\n" \
               f"state: {self.comm_state.name}\n" \
               f"expected food at: ({round(self.pos[0] + rotate(self.behavior.navigation_table.get_relative_position_for_location(Location.FOOD), self.orientation)[0])}, {round(self.pos[1] + rotate(self.behavior.navigation_table.get_relative_position_for_location(Location.FOOD), self.orientation)[1])}), \n" \
               f"   known: {self.behavior.navigation_table.is_information_valid_for_location(Location.FOOD)}\n" \
               f"expected nest at: ({round(self.pos[0] + rotate(self.behavior.navigation_table.get_relative_position_for_location(Location.NEST), self.orientation)[0])}, {round(self.pos[1] + rotate(self.behavior.navigation_table.get_relative_position_for_location(Location.NEST), self.orientation)[1])}), \n" \
               f"   known: {self.behavior.navigation_table.is_information_valid_for_location(Location.NEST)}\n" \
               f"info age:\n" \
               f"   -food={round(self.behavior.navigation_table.get_information_entry(Location.FOOD).age, 3)}\n" \
               f"   -nest={round(self.behavior.navigation_table.get_information_entry(Location.NEST).age, 3)}\n" \
               f"carries food: {self._carries_food}\n" \
               f"drift: {round(self.noise_mu, 5)}\n" \
               f"reward: {round(self.environment.payment_database.get_reward(self.id), 3)}$\n" \
               f"item count: {self.items_collected}\n" \
               f"dr: {np.round(self.dr, 2)}\n" \
               f"{self.behavior.debug_text()}"


    def __repr__(self):
        return f"bot {self.id}"


    def __hash__(self):
        return self.id


    def __eq__(self, other):
        return self.id == other.id


    def __ne__(self, other):
        return not (self == other)


    def communicate(self, neighbors):
        self.previous_nav = copy.deepcopy(self.behavior.navigation_table)
        if self.comm_state == CommunicationState.OPEN:
            session = CommunicationSession(self, neighbors)
            if self.behavior.required_information==RequiredInformation.LOCAL:
                self.behavior.buy_info(None,session)
            elif self.behavior.required_information==RequiredInformation.GLOBAL:    
                self.behavior.buy_info(self.environment.payment_database,session)
        self.new_nav = self.behavior.navigation_table
        self.behavior.navigation_table = self.previous_nav


    def step(self):
        self.behavior.navigation_table = self.new_nav
        self.sensors = self.environment.get_sensors(self)
        
        if not self.comm_state == CommunicationState.PROCESSING:
            self.behavior.step(AgentAPI(self))
            try:
                self.environment.payment_database.apply_cost(self.id, self.fuel_cost)
                self.move()
            except InsufficientFundsException:
                pass
        # if self.carries_food: self.increase_exipration_timer()#[x]IEFM
        self.update_communication_state()
        self.update_trace()


    def get_info_from_behavior(self, location):
        return self.behavior.sell_info(location)


    def update_trace(self):
        self.trace.appendleft(self.pos[1])
        self.trace.appendleft(self.pos[0])


    def get_relative_position_to_location(self, location: Location):
        if self.environment.get_sensors(self)[location]:
            return rotate(self.environment.get_location(location, self) - self.pos, -self.orientation)
        else:
            raise NoLocationSensedException()


    def move(self):
        """
        if self.bimodal_noise: sample motion angle from a probability distribution
        else: linearly incremented motion angle wrt robot_id_i/max(robot_id_j), starting from mean,
             with slope such that last one has 99% value of a normal distribution with same mean and sd
               
        """
        wanted_movement = rotate(self.dr, self.orientation)
        if self.bimodal_noise:
            noise_angle = gauss(self.noise_mu, self.noise_sd)
        else:
            gauss(0,0)  # discard this r.n.
            noise_angle = self.noise_mu
        noisy_movement = rotate(wanted_movement, noise_angle)
        self.orientation = get_orientation_from_vector(noisy_movement)
        self.pos = self.clamp_to_map(self.pos + noisy_movement)


    def clamp_to_map(self, new_position):
        if new_position[0] < self._radius:
            new_position[0] = self._radius
        if new_position[1] < self._radius:
            new_position[1] = self._radius
        if new_position[0] > self.environment.width - self._radius:
            new_position[0] = self.environment.width - self._radius
        if new_position[1] > self.environment.height - self._radius:
            new_position[1] = self.environment.height - self._radius
        return new_position


    def update_levi_counter(self):
        self.levi_counter -= 1
        if self.levi_counter <= 0:
            self.levi_counter = choices(range(1, rw.get_max_levi_steps() + 1), rw.get_levi_weights())[0]


    def get_levi_turn_angle(self):
        angle = 0
        if self.levi_counter <= 1:
            angle = choices(np.arange(0, 360), rw.get_crw_weights())[0]
        self.update_levi_counter()
        return angle


    def draw(self, canvas):
        circle = canvas.create_oval(self.pos[0] - self._radius,
                                    self.pos[1] - self._radius,
                                    self.pos[0] + self._radius,
                                    self.pos[1] + self._radius,
                                    fill=self.behavior.color,
                                    outline=self.colors[self.behavior.state],
                                    width=3)
        self.draw_comm_radius(canvas)
        # self.draw_goal_vector(canvas)
        self.draw_orientation(canvas)
        # self.draw_trace(canvas)


    def draw_trace(self, canvas):
        tail = canvas.create_line(*self.trace)


    def draw_comm_radius(self, canvas):
        circle = canvas.create_oval(self.pos[0] - self.communication_radius,
                                    self.pos[1] - self.communication_radius,
                                    self.pos[0] + self.communication_radius,
                                    self.pos[1] + self.communication_radius,
                                    outline="gray")


    def draw_goal_vector(self, canvas):
        pass
        #OVERLOADED IN gui.py
        # arrow = canvas.create_line(self.pos[0],
        #                            self.pos[1],
        #                            self.pos[0] + rotate(
        #                                self.behavior.navigation_table.get_relative_position_for_location(Location.FOOD),
        #                                self.orientation)[0],
        #                            self.pos[1] + rotate(
        #                                self.behavior.navigation_table.get_relative_position_for_location(Location.FOOD),
        #                                self.orientation)[1],
        #                            arrow=LAST,
        #                            fill="darkgreen")
        # arrow = canvas.create_line(self.pos[0],
        #                            self.pos[1],
        #                            self.pos[0] + rotate(
        #                                self.behavior.navigation_table.get_relative_position_for_location(Location.NEST),
        #                                self.orientation)[0],
        #                            self.pos[1] + rotate(
        #                                self.behavior.navigation_table.get_relative_position_for_location(Location.NEST),
        #                                self.orientation)[1],
        #                            arrow=LAST,
        #                            fill="darkorange")


    def draw_orientation(self, canvas):
        line = canvas.create_line(self.pos[0],
                                  self.pos[1],
                                  self.pos[0] + self._radius * cos(radians(self.orientation)),
                                  self.pos[1] + self._radius * sin(radians(self.orientation)),
                                  fill="white")


    def speed(self):
        return self._speed


    def radius(self):
        return self._radius


    def get_id(self):
        return self.id


    def reward(self):
        return self.environment.payment_database.get_reward(self.id)


    def get_sensors(self):
        return self.sensors


    def carries_food(self):
        return self._carries_food


    def drop_food(self):
        self._carries_food = False
        self.items_collected += 1
        # self._expiration_timer=0#[x]IEFM


    def pickup_food(self):
        self._carries_food = True


    def set_desired_movement(self, dr):
        norm_dr = norm(dr)
        if norm_dr > self._speed:
            dr = self._speed * dr / norm_dr
        self.dr = dr


    def record_transaction(self,type:str,seller_id:int=None,transaction:Transaction=None):
        if type=="attempted" or type=="a" or type=="A" or \
                type=="validated" or type=="v" or type=="V" or \
                type=="combined" or type=="x" or type=="X":
            self.environment.payment_database.record_transaction(type,self.id,seller_id)
        elif type=="completed" or type=="c" or type=="C":
            transaction.timestep = self.environment.timestep
            self.environment.payment_database.record_transaction(type,self.id,seller_id,transaction)
        else:
            raise ValueError("Transaction type not recognized")


    def update_communication_state(self):
        self._time_since_last_comm += 1
        if self._time_since_last_comm > self._comm_stop_time + self._communication_cooldown:
            self.comm_state = CommunicationState.OPEN
        elif self._time_since_last_comm > self._comm_stop_time:
            self.comm_state = CommunicationState.ON_COOLDOWN
        else:
            self.comm_state = CommunicationState.PROCESSING


    def communication_happened(self):
        self._time_since_last_comm = 0


    #[x]IEFM
    # def increase_exipration_timer(self):
    """
    
        if self._carries_food:
            self._food_expiration_time += 1
        elif self._food_expiration_time > 0:
            self._food_expiration_time = 0
    """
    #     self._expiration_timer += 1

    
    # def get_expiration_timer(self):
    #     return self._expiration_timer