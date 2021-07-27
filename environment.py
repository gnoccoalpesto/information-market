from agent import Agent
from random import randint


class Environment:

    def __init__(self, width=500, height=500, nb_robots=30, robot_speed=3, robot_radius=5, rdwalk_factor=0,
                 food_x=0, food_y=0, food_radius=25, nest_x=500, nest_y=500, nest_radius=25):
        self.population = list()
        self.width = width
        self.height = height
        self.nb_robots = nb_robots
        self.robot_speed = robot_speed
        self.robot_radius = robot_radius
        self.rdwalk_factor = rdwalk_factor
        self.food = (food_x, food_y, food_radius)
        self.nest = (nest_x, nest_y, nest_radius)
        self.create_robots()

    def step(self):
        for robot in self.population:
            robot.step()

    def create_robots(self):
        for robot_id in range(self.nb_robots):
            robot = Agent(robot_id=robot_id,
                          x=randint(self.robot_radius, self.width-1-self.robot_radius),
                          y=randint(self.robot_radius, self.height-1-self.robot_radius),
                          speed=self.robot_speed,
                          radius=self.robot_radius,
                          rdwalk_factor=self.rdwalk_factor,
                          environment=self)
            self.population.append(robot)

    def check_border_collision(self, robot, new_x, new_y):
        collide_x = False
        collide_y = False
        if new_x+robot.radius >= self.width or new_x-robot.radius < 0:
            collide_x = True

        if new_y+robot.radius >= self.height or new_y-robot.radius < 0:
            collide_y = True

        return collide_x, collide_y

    def senses_food(self, robot):
        dist_from_center = (robot.x - self.food[0])**2 + (robot.y - self.food[1])**2
        return dist_from_center < self.food[2]**2

    def senses_nest(self, robot):
        dist_from_center = (robot.x - self.nest[0]) ** 2 + (robot.y - self.nest[1]) ** 2
        return dist_from_center < self.nest[2] ** 2

    def get_food_location(self):
        return self.food[0], self.food[1]

    def get_nest_location(self):
        return self.nest[0], self.nest[1]

    def draw(self, canvas):
        self.draw_zones(canvas)
        for robot in self.population:
            robot.draw(canvas)

    def draw_zones(self, canvas):
        food_circle = canvas.create_oval(self.food[0] - self.food[2],
                                    self.food[1] - self.food[2],
                                    self.food[0] + self.food[2],
                                    self.food[1] + self.food[2],
                                    fill="green")
        nest_circle = canvas.create_oval(self.nest[0] - self.nest[2],
                                         self.nest[1] - self.nest[2],
                                         self.nest[0] + self.nest[2],
                                         self.nest[1] + self.nest[2],
                                         fill="orange")
