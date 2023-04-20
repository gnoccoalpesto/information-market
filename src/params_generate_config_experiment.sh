#!/bin/bash

# experiment variable params for automatic config generator
# see src/generate_config.py for more info

#EXPERIMENT PARAMETERS: MODIFY AS YOU WILL #################################################
# ----------------- NOTE LISTS MUST BE IN THIS FORMAT: (value1 ... valueN) --------------- #
# ----------------- NOTE BOOLs = {true, false} ------------------------------------------- #

#simulation
SIMULATION_STEPS=15000
SIMULATION_SEED=5684436
NUMBER_RUNS=20
#visualisation
VISUALISATION_ACTIVATE=false
#noise
AGENT_NOISE_ASSIGNATION_LIST=("average" 
							"perfect"
							)
# bimodal:
AGENT_NOISE_SAMPLING_MU_LIST=(0.05)
AGENT_NOISE_SAMPLING_SIGMA_LIST=(0.05)
AGENT_NOISE_SD_LIST=(0.05)
# (uniform:) average, perfect:
AGENT_NOISE_MU_LIST=(0.051)
AGENT_NOISE_RANGE_LIST=(0.1)
#combine_strategy
COMBINE_STRATEGY_LIST=(
						"waa"
						# "nfwar" 
						# "fwar" 
						# "nrwar" 
						# "wara"
						)
#payment system
PAYMENT_SYSTEM_CLASS_LIST=(
							"OutlierPenalisationPaymentSystem" 
							"DelayedPaymentPaymentSystem"
							)
#data collection
DATA_PRECISE_RECORDING_INTERVAL=100
DATA_TRANSACTIONS_LOG=false
#robots
NUMBER_OF_ROBOTS=25
HONEST_POPULATION_LIST=(24)
DISHONEST_LIE_ANGLES=(90)
# behaviors ----------------------------------------------------
BEHAVIOR_LIST=(
				"n" "s"
				"r" 
				"t" 
				"Nv"
				"w"
			)
# naive: n ; new naive: Nn ; wealth weighted: w
################################################ -params:{}
# sceptical: s ; new sceptical: Ns
################################## -params:{threshold} ; {scepticism_threshold}
sSCEPTICISM_THRESHOLD_LIST=(0.25)
# ranking: r
############ -params:{ranking_threshold}
rRANKING_THRESHOLD_LIST=(
						0.3 
						0.5
						)
# variable scepticism: v ; new variable scepticism: Nv
###################################################### -params:{comparison_method,scaling,scepticism_threshold,weight_method}
vCOMPARISON_METHOD_LIST=("allavg" "allmax")
vSCALING_LIST=(0.8 0.5 0.3)
vSCEPTICISM_THRESHOLD_LIST=(0.25)
vWEIGHT_METHOD_LIST=("ratio" "exponential")
# wealth threshold: t
##################### -params:{comparison_method,scaling}
tCOMPARISON_METHOD_LIST=("allavg" "allmax")
tSCALING_LIST=(0.8 0.5 0.3)
