#!/bin/bash

# fixed params for automatic config generator
# see src/generate_config.py for more info


#GENERAL PARAMETERS ####################################################
# - DO NOT MODIFY,  UNLESS YOU WANT TO INTRODUCE ENVIRONMENT CHANGES - #

#environment
WIDTH=1200
HEIGHT=600

#food
FOOD_X=200
FOOD_Y=300
FOOD_RADIUS=50

#nest
NEST_X=1000
NEST_Y=300
NEST_RADIUS=50

#visualisation
VISUALISATION_FPS=60

#random walk
RANDOM_WALK_FACTOR=0.9
RANDOM_WALK_LEVI_FACTOR=1.4

#agent
AGENT_RADIUS=8
AGENT_SPEED=2.5
AGENT_COMMUNICATION_RADIUS=50
AGENT_COMMUNICATION_STOP_TIME=0
AGENT_COMMUNICATION_COOLDOWN=0
AGENT_FUEL_COST=0
