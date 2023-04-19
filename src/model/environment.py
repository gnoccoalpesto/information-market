from math import cos, sin, radians
from random import randint, random, seed as random_seed
import numpy as np

from model.agent import Agent
from model.market import market_factory
from model.navigation import Location
from helpers.utils import norm, distance_between
from model.payment import PaymentDB


def random_seeder(seed,n=None):
    """
    applies the random.seed using input, when seed is not None
    """
    if seed!="" and seed!="random" and seed is not None:
        random_seed(seed+n if n is not None else seed)

def generate_uniform_noise_list(n_robots,n_dishonest,dishonest_noise_performance,
                                noise_mu, noise_range,
                                random_switch=False,random_seed=None):
    """
    generates a list of fixed noise to directly assign in the case of
    noise not drawed from a bimodal distribution
    noise is generated, increasing with agent_id, s.t. last one has a value covering 
        99% (coverage_coeff==2.3) of the previous bimodal distribution values
    :param dishonest position: informs the generator how much noise dishonests agent will have:
        -"average": d. have average noise,
        -"perfect": d. have lowest noise,
        -"worst": d. have highest noise

    return value is always ordered wrt robots_id, but will have different values
    based on range, and dishonest_noise_performance request
    """
    def generate_noise(mu, range, robot_id,total_robots,random_switch):
        central_id=total_robots//2
        if robot_id<=central_id:
            sampled=round(mu-range*(central_id-robot_id)/total_robots,4)
        else:
            sampled=round(mu+range*(robot_id-central_id)/total_robots,4)
        if random_switch:
            if random()<0.5:sampled=-sampled
        return sampled
    
    if dishonest_noise_performance=="average":
        "eg 6robots, 2 d: 2,3,4,5,6,0,1"
        rounded_n_honests=n_robots//2-2
        generation_list=[_ for _ in [_ for _ in range(rounded_n_honests)]+
                                    [_ for _ in range(rounded_n_honests+n_dishonest,n_robots)]+
                                    [_ for _ in range(rounded_n_honests,rounded_n_honests+n_dishonest)]]
    elif dishonest_noise_performance=="perfect":
        #heuristic for perfect saboteur in conditions around nominal: mean=0.05, range=0.1-0.14
        ids_negative_value_dict={"0.1":int(200*(0.05-noise_mu)),
                                "0.15":n_robots//7,
                                "0.2":n_robots//5}
        try:    
            ids_negative_value=ids_negative_value_dict[str(noise_range)]
        except KeyError:
            if noise_range>0.1 and noise_range<0.15:
                ids_negative_value=int((ids_negative_value_dict["0.15"]+ids_negative_value_dict["0.1"])//2)
            elif noise_range>0.15 and noise_range<0.2:
                ids_negative_value=int((ids_negative_value_dict["0.2"]+ids_negative_value_dict["0.15"])//2)
            elif noise_range>0.2:
                ids_negative_value=n_robots//3

        "eg 6robots, 2 d: 0,1,2,3,4,5,6"
        generation_list=[_ for _ in [_ for _ in range(ids_negative_value)]+
                                    [_ for _ in range(ids_negative_value+n_dishonest,n_robots)]+
                                    [_ for _ in range(ids_negative_value,ids_negative_value+n_dishonest)]]
    random_seeder(random_seed)
    noise_list=[generate_noise(noise_mu,
                            noise_range,
                            robot_id,
                            n_robots,
                            random_switch) 
                for robot_id in generation_list ]
    return noise_list
    

class Environment:
    def __init__(self,
                 width,
                 height, 
                 agent_params, 
                 behavior_params,
                 combine_strategy_params,
                 food, 
                 nest, 
                 payment_system_params, 
                 market_params,
                 simulation_seed=None
                 ):
        self.population = list()
        self.ROBOTS_AMOUNT=0
        self.width = width
        self.height = height
        self.food = (food['x'], food['y'], food['radius'])
        self.nest = (nest['x'], nest['y'], nest['radius'])
        self.locations = {Location.FOOD: self.food, Location.NEST: self.nest}
        self.foraging_spawns = self.create_spawn_dicts()
        self.SIMULATION_SEED=simulation_seed
        self.create_robots(agent_params, behavior_params,combine_strategy_params)
        self.best_bot_id = self.get_best_bot_id()
        self.payment_database = PaymentDB([bot.id for bot in self.population], payment_system_params)
        self.market = market_factory(market_params)
        self.img = None
        self.timestep = 0


    def step(self):
        self.timestep += 1
        for robot in self.population:
            self.payment_database.increment_wallet_age(robot.id)
        # compute neighbors
        pop_size = len(self.population)
        neighbors_table = [[] for i in range(pop_size)]
        for id1 in range(pop_size):
            for id2 in range(id1 + 1, pop_size):
                if distance_between(self.population[id1], self.population[id2]) < self.population[id1].communication_radius:
                    neighbors_table[id1].append(self.population[id2])
                    neighbors_table[id2].append(self.population[id1])
        # 1. Negotiation/communication
        for robot in self.population:
            robot.communicate(neighbors_table[robot.id])
        # 2. Movement
        for robot in self.population:
            self.check_locations(robot)
            robot.step()
        # 3. Market
        self.market.step()


    def load_images(self):
        pass
        #OVERLOADED IN gui.py
        # self.img = ImageTk.PhotoImage(file="../assets/strawberry.png")


    def create_robots(self, agent_params, behavior_params,combine_strategy_params):
        robot_id = 0
        self.ROBOTS_AMOUNT = np.sum([behavior['population_size'] for behavior in behavior_params])
        self.DISHONEST_AMOUNT = int(np.sum([behavior['population_size'] for behavior in behavior_params
                                     if "teur" in behavior['class']]))#TODO check instead in a list of saboteurs behav
        if agent_params["noise"]["class"]=="UniformNoise":
            generated_fixed_noise=generate_uniform_noise_list(self.ROBOTS_AMOUNT,
                                                         self.DISHONEST_AMOUNT,
                                                            agent_params["noise"]["parameters"]["dishonest_noise_performance"],
                                                            agent_params["noise"]["parameters"]["noise_mu"],
                                                            agent_params["noise"]["parameters"]["noise_range"],
                                                            random_switch=True,
                                                            random_seed=self.SIMULATION_SEED*20
                                                    )
        random_seeder(self.SIMULATION_SEED)#no need to waste samples if not random_switch      
        for behavior_params in behavior_params:
            behavior_params["parameters"]["combine_strategy"]=combine_strategy_params["class"]
            for _ in range(behavior_params['population_size']):

                if agent_params["noise"]["class"]=="UniformNoise":
                    agent_params["noise"]["parameters"]["noise_mu"] = generated_fixed_noise[robot_id]

                robot_x=randint(agent_params['radius'], self.width - 1 - agent_params['radius'])
                robot_y=randint(agent_params['radius'], self.height - 1 - agent_params['radius'])
                robot = Agent(robot_id=robot_id,
                              x=robot_x,
                              y=robot_y,
                              environment=self,
                              behavior_params=behavior_params,
                              **agent_params)
                robot_id += 1
                self.population.append(robot)


    def get_sensors(self, robot):
        orientation = robot.orientation
        speed = robot.speed()
        sensors = {Location.FOOD: self.senses(robot, Location.FOOD),
                   Location.NEST: self.senses(robot, Location.NEST),
                   #TODO any() in check_border_collision, is this causing WARNING?
                   "FRONT": any(self.check_border_collision(robot, robot.pos[0] + speed * cos(radians(orientation)),
                                                            robot.pos[1] + speed * sin(radians(orientation)))),
                   "RIGHT": any(
                       self.check_border_collision(robot, robot.pos[0] + speed * cos(radians((orientation - 90) % 360)),
                                                   robot.pos[1] + speed * sin(radians((orientation - 90) % 360)))),
                   "BACK": any(self.check_border_collision(robot, robot.pos[0] + speed * cos(
                       radians((orientation + 180) % 360)),
                                                           robot.pos[1] + speed * sin(
                                                               radians((orientation + 180) % 360)))),
                   "LEFT": any(
                       self.check_border_collision(robot, robot.pos[0] + speed * cos(radians((orientation + 90) % 360)),
                                                   robot.pos[1] + speed * sin(radians((orientation + 90) % 360)))),
                   }
        return sensors


    def senses(self, robot:Agent, location:Location):
        dist_vector = robot.pos - np.array([self.locations[location][0], self.locations[location][1]])
        dist_from_center = np.sqrt(dist_vector.dot(dist_vector))
        return dist_from_center < self.locations[location][2]


    def check_border_collision(self, robot:Agent, new_x, new_y):
        collide_x = False
        collide_y = False
        if new_x + robot._radius >= self.width or new_x - robot._radius < 0:
            collide_x = True
        if new_y + robot._radius >= self.height or new_y - robot._radius < 0:
            collide_y = True
        # return any([collide_x, collide_y])
        return collide_x, collide_y


    def is_on_top_of_spawn(self, robot:Agent, location:Location):
        dist_vector = robot.pos - self.foraging_spawns[location].get(robot.id)
        return np.sqrt(dist_vector.dot(dist_vector)) < robot._radius


    def get_location(self, location:Location, agent:Agent):
        if agent.id in self.foraging_spawns[location]:
            return self.foraging_spawns[location][agent.id]
        else:
            return np.array([self.locations[location][0], self.locations[location][1]])


    def draw(self, canvas):
        self.draw_zones(canvas)
        self.draw_strawberries(canvas)
        for robot in self.population:
            robot.draw(canvas)
        # self.draw_best_bot(canvas)


    def draw_market_stats(self, stats_canvas):
        margin = 15
        width = stats_canvas.winfo_width() - 2 * margin
        height = 20
        stats_canvas.create_rectangle(margin, 50, margin + width, 50 + height, fill="light green", outline="")
        target_demand = self.market.demand
        max_theoretical_supply = self.market.demand/self.demand
        demand_pos_x = width*target_demand/max_theoretical_supply
        supply_pos_x = width*self.market.get_supply()/max_theoretical_supply
        supply_bar_width = 2
        stats_canvas.create_rectangle(margin + demand_pos_x, 50, margin + width, 50 + height, fill="salmon", outline="")
        stats_canvas.create_rectangle(margin + supply_pos_x - supply_bar_width/2, 48, margin + supply_pos_x + supply_bar_width/2, 52 + height, fill="gray45", outline="")
        stats_canvas.create_text(margin + supply_pos_x - 5, 50 + height + 5, fill="gray45", text=f"{round(self.market.get_supply())}", anchor="nw", font="Arial 10")


    def draw_zones(self, canvas):
        food_circle = canvas.create_oval(self.food[0] - self.food[2],
                                         self.food[1] - self.food[2],
                                         self.food[0] + self.food[2],
                                         self.food[1] + self.food[2],
                                         fill="green",
                                         outline="")
        nest_circle = canvas.create_oval(self.nest[0] - self.nest[2],
                                         self.nest[1] - self.nest[2],
                                         self.nest[0] + self.nest[2],
                                         self.nest[1] + self.nest[2],
                                         fill="orange",
                                         outline="")


    def draw_strawberries(self, canvas):
        for bot_id, pos in self.foraging_spawns[Location.FOOD].items():
            canvas.create_image(pos[0] - 8, pos[1] - 8, image=self.img, anchor='nw')


    def draw_best_bot(self, canvas):
        circle = canvas.create_oval(self.population[self.best_bot_id].pos[0] - 4,
                                    self.population[self.best_bot_id].pos[1] - 4,
                                    self.population[self.best_bot_id].pos[0] + 4,
                                    self.population[self.best_bot_id].pos[1] + 4,
                                    fill="red")


    def get_best_bot_id(self):
        best_bot_id = 0
        for bot in self.population:
            if 1 - abs(bot.noise_mu) > 1 - abs(self.population[best_bot_id].noise_mu):
                best_bot_id = bot.id
        return best_bot_id


    def get_robot_at(self, x, y):
        selected = None
        for bot in self.population:
            if norm(bot.pos - np.array([x, y]).astype('float64')) < bot.radius():
                selected = bot
                break
        return selected


    def get_robot_by_id(self, id):
        selected = None
        for bot in self.population:
            if bot.id == id:
                selected = bot
                break
        return selected


    @staticmethod
    def create_spawn_dicts():
        d = dict()
        for location in Location:
            d[location] = dict()
        return d


    def check_locations(self, robot:Agent):
        if robot.carries_food():
            if self.senses(robot, Location.NEST):
                # Spawn deposit location if needed
                if robot.id not in self.foraging_spawns[Location.NEST]:
                    self.add_spawn(Location.NEST, robot)
                # Check if robot can deposit food
                if self.is_on_top_of_spawn(robot, Location.NEST):
                    self.deposit_food(robot)
        else:
            if self.senses(robot, Location.FOOD):
                # Spawn food if needed
                if robot.id not in self.foraging_spawns[Location.FOOD]:
                    self.add_spawn(Location.FOOD, robot)
                # Check if robot can pickup food
                if self.is_on_top_of_spawn(robot, Location.FOOD):
                    self.pickup_food(robot)


    def add_spawn(self, location:Location, robot:Agent):
        rand_angle = random() * 360
        rand_rad = np.sqrt(random()) * self.locations[location][2]
        pos_in_circle = rand_rad * np.array([cos(radians(rand_angle)), sin(radians(rand_angle))])
        self.foraging_spawns[location][robot.id] = np.array([self.locations[location][0],
                                                             self.locations[location][1]]) + pos_in_circle


    def deposit_food(self, robot:Agent):
        robot.drop_food()
        self.foraging_spawns[Location.NEST].pop(robot.id)

        reward = self.market.sell_strawberry(robot.id)

        self.payment_database.pay_reward(robot.id, reward=reward)
        self.payment_database.pay_creditors(robot.id, total_reward=reward)


    def pickup_food(self, robot):
        robot.pickup_food()
        self.foraging_spawns[Location.FOOD].pop(robot.id)