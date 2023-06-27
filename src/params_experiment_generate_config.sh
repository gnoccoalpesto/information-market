#!/bin/bash

# experiment variable params for automatic config generator
# see src/generate_config.py for more info

#EXPERIMENT PARAMETERS: MODIFY AS YOU WILL #################################################
# ----------------- NOTE LISTS MUST BE IN THIS FORMAT: (value1 ... valueN) --------------- #
# ----------------- NOTE BOOLs = {true, false} ------------------------------------------- #

#simulation
SIMULATION_STEPS=25000
SIMULATION_SEED=5684436
NUMBER_RUNS=20
#visualisation
VISUALISATION_ACTIVATE=false
#noise
AGENT_NOISE_ASSIGNATION_LIST=(
							"average" 
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
							# "DelayedPaymentPaymentSystem"
							)
PAYMENT_SYSTEM_REPUTATION_STAKE_LIST=(
										false
										true
)
#data collection
DATA_PRECISE_RECORDING_INTERVAL=100
DATA_TRANSACTIONS_LOG=false
#robots
NUMBER_OF_ROBOTS=25
HONEST_POPULATION_LIST=(
							20
							17
							22
							25
							24
						)
DISHONEST_LIE_ANGLE_LIST=(
						0 
						90
					)
# behaviors ----------------------------------------------------
BEHAVIOR_LIST=(
				"b"
				"n"
				"s"
				"r" 
				"t" 
				"c"
				# "Nv"
				# "h"
				# "hs"
			)

# benchmark: b
############## -params:{good_acceptance_rate,bad_acceptance_rate,saboteur_acceptance_rate}
bGOOD_ACCEPTANCE_RATE_LIST=(
							0.75
							0.85
							0.95
							)
bBAD_ACCEPTANCE_RATE_LIST=(
							0.55
							0.4
							0.25
							)
bSABOTEUR_ACCEPTANCE_RATE_LIST=(
								0.15
								0.075
								0
								)
			
# naive: n ; new naive: Nn 
################################################ -params:{}

# sceptical: s ; new sceptical: Ns
################################## -params:{threshold} ; {scepticism_threshold}
sSCEPTICISM_THRESHOLD_LIST=(0.25)

# capitalist: c
################# -params:{reputation_method}
cREPUTATION_METHOD_LIST=(
						"r"
						"t"
						)

# ranking: r
############ -params:{ranking_threshold}
rRANKING_THRESHOLD_LIST=(
						0.3 
						0.5
						)
rREPUTATION_METHOD_LIST=(
						"r"
						"t"
						)

# wealth threshold: t
##################### -params:{comparison_method,scaling}
tCOMPARISON_METHOD_LIST=(
							"allavg" 
							# "allmax"
							)
tSCALING_LIST=(
				0.8 	
				0.5 
				# 0.3
				)
tREPUTATION_METHOD_LIST=(
						"r"
						"t"
						)

# reputation history: h
######################## -params:{verification_method,threshold_method}
hVERIFICATION_METHOD_LIST=(
							"discrete" 
							# "difference" 
							# "recency" 
							# "aged" 
							# "aged2"
						)
hTHRESHOLD_METHOD_LIST=(
						# # "positive" 
						"mean"
						)
hSCALING_LIST=(
				1
				# 0.8 
				# 0.5 
				# 0.3
				)
hKD_LIST=(
			# 0.7
			1
			# 1.3
			# 1.6
			# 2.0
)
hREPUTATION_METHOD_LIST=(
						"h"
						)
						
# reputation history scepticism: hs
######################## -params:{verification_method,threshold_method}
hsVERIFICATION_METHOD_LIST=(
							"discrete" 
							# "difference" 
							# "recency" 
							# "aged" 
							# "aged2"
						)
hsTHRESHOLD_METHOD_LIST=(
						# # "positive" 
						"mean"
						)
hsSCALING_LIST=(
				1
				# 0.8 
				# 0.5 
				# 0.3
				)
hsKD_LIST=(
			# 0.7
			1
			# 1.3
			# 1.6
			# 2.0
)
hsSCEPTICISM_THRESHOLD_LIST=(0.25)

# variable scepticism: v ; new variable scepticism: Nv
###################################################### -params:{comparison_method,scaling,scepticism_threshold,weight_method}
vCOMPARISON_METHOD_LIST=(
							"allavg" 
							# "allmax"
							)
vSCALING_LIST=(
				# 0.8 
				# 0.5 
				0.3
				)
vSCEPTICISM_THRESHOLD_LIST=(0.25)
vWEIGHT_METHOD_LIST=(
						"ratio" 
						# "exponential"
						)