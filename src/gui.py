from tkinter import LAST
from PIL import ImageTk
from helpers.utils import rotate

from model.navigation import Location
from controllers.main_controller import MainController, Configuration
from controllers.view_controller import ViewController
from info_market import InformationMarket
from model.environment import Environment
from model.agent import Agent

'''
REDEFINITION OF ALL THE CLASSES' METHODS USING/CONTRIBUTING TO THE GUI INTERFACE

NOTE: the redefinition is just a way to avoid annoying warnings, without deactivating them
'''

class InformationMarket(InformationMarket):
    @staticmethod
    def launch_view_controller(main_controller:MainController,c:Configuration):
        return ViewController(main_controller,
                                        c.value_of("width"),
                                        c.value_of("height"),
                                        c.value_of("visualization")['fps']
                                        )


class Environment(Environment):
    def load_images(self):
        self.img = ImageTk.PhotoImage(file="../assets/strawberry.png")


class Agent(Agent):
    def draw_goal_vector(self, canvas):
        arrow = canvas.create_line(self.pos[0],
                                   self.pos[1],
                                   self.pos[0] + rotate(
                                       self.behavior.navigation_table.get_relative_position_for_location(Location.FOOD),
                                       self.orientation)[0],
                                   self.pos[1] + rotate(
                                       self.behavior.navigation_table.get_relative_position_for_location(Location.FOOD),
                                       self.orientation)[1],
                                   arrow=LAST,
                                   fill="darkgreen")
        arrow = canvas.create_line(self.pos[0],
                                   self.pos[1],
                                   self.pos[0] + rotate(
                                       self.behavior.navigation_table.get_relative_position_for_location(Location.NEST),
                                       self.orientation)[0],
                                   self.pos[1] + rotate(
                                       self.behavior.navigation_table.get_relative_position_for_location(Location.NEST),
                                       self.orientation)[1],
                                   arrow=LAST,
                                   fill="darkorange")

################################################################################################
################################################################################################
################################################################################################
if __name__ == '__main__':
    infomarket=InformationMarket()