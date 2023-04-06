#!/bin/bash

# automatically generates multiple config file for the information market simulation
# all the permitted (wrt behaviour.py) combinations of parameters are generated
# the generated config files are stored in the CONFIG_DIR directory
# config files are named according to the parameters they contain
# filename of results of configurations runs are identical to the config file name
# OPTIONALLY, can pass a parameter to create a subdirectory in the data directory
#             for the current experiment
#
# usage: ./generate_config.sh [subdirectory_name]

PROJECT_HOME="${HOME}/information-market/"
CONFIG_DIR="${PROJECT_HOME}config/"
ASSETS_DIR="${PROJECT_HOME}assets/"
EXEC_FILE="${PROJECT_HOME}src/info_market.py"
DATA_DIR="${PROJECT_HOME}data/CLUSTER/"
# DATA_DIR="${PROJECT_HOME}data/"
if [ $# -ne 0 ]; then
  DATA_DIR="${DATA_DIR}$1/"
fi

CONFIG_FILE_TEMPLATE="${ASSETS_DIR}config_template"
# CONFIG_FILE_TEMPLATE="${CONFIG_DIR}config_template"


# --- PLEASE REFER TO README FOR MORE INFORMATION ON THE PARAMETERS --- #


#GENERAL PARAMETERS ####################################################
# -- DO NOT MODIFY, UNLESS YOU WANT TO INTRODUCE ENVIRONMENT CHANGES - #

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

#payment system
PAYMENT_SYSTEM_INITIAL_REWARD=1
PAYMENT_SYSTEM_INFORAMTION_SHARE=0.5

#market
MARKET_CLASS="FixedPriceMarket"
MARKET_REWARD=1


#EXPERIMENT PARAMETERS: MODIFY AS YOU WILL #################################################
# ----------------- NOTE LISTS MUST BE IN THIS FORMAT: (value1 ... valueN) --------------- #

#simulation
SIMULATION_STEPS=15000
SIMULATION_SEED=5684436
NUMBER_RUNS=20

#visualisation
VISUALISATION_ACTIVATE=false

#noise
AGENT_NOISE_ASSIGNATION_LIST=("bimodal" "average" "perfect")
# RANDOM: "bimodal"; FIXED: "average" "perfect" (saboteur performance)
# bimodal:
AGENT_NOISE_SAMPLING_MU_LIST=(0.05)
AGENT_NOISE_SAMPLING_SIGMA_LIST=(0.05)
AGENT_NOISE_SD_LIST=(0.05)
# average, perfect:
AGENT_NOISE_MU_LIST=(0.051)
AGENT_NOISE_RANGE_LIST=(0.1 0.14)

#payment system
# PAYMENT_SYSTEM_CLASS=("OutlierPenalisationPaymentSystem")
# PAYMENT_SYSTEM_CLASS=("DelayedPaymentPaymentSystem")
PAYMENT_SYSTEM_CLASS_LIST=("OutlierPenalisationPaymentSystem" "DelayedPaymentPaymentSystem")

#data collection
DATA_PRECISE_RECORDING_INTERVAL=100
DATA_TRANSACTIONS_LOG=false

#robots
NUMBER_OF_ROBOTS=25
HONEST_POPULATION_LIST=(24)
DISHONEST_LIE_ANGLES=(90)


# behaviors ----------------------------------------------------
BEHAVIOR_LIST=("n" "s" "r" "Nv" "t" "w")

# naive: n ; new naive: Nn ; wealth weighted: w
# -params:{}

# sceptical: s ; new sceptical: Ns
# -params:{threshold} ; {scepticism_threshold}
sSCEPTICISM_THRESHOLD_LIST=(0.25)

# ranking: r
# -params:{ranking_threshold}
rRANKING_THRESHOLD_LIST=(0.3 0.5)

# variable scepticism: v ; new variable scepticism: Nv
# -params:{comparison_method,scaling,scepticism_threshold,weight_method}
vCOMPARISON_METHOD_LIST=("allavg" "allmax")
vSCALING_LIST=(0.8 0.5 0.3)
vSCEPTICISM_THRESHOLD_LIST=(0.25)
vWEIGHT_METHOD_LIST=("ratio" "exponential")

# wealth threshold: t
# -params:{comparison_method,scaling}
tCOMPARISON_METHOD_LIST=("allavg" "allmax")
tSCALING_LIST=(0.8 0.5 0.3)


# PARAMETERS DICTIONARIES #######################################################
# ----------------- DO NOT MODIFY, UNLESS YOU MODIFY behaviour.py ------------- #

# behavior
declare -A HONEST_DICTIONARY
	HONEST_DICTIONARY[n]="NaiveBehavior"
	HONEST_DICTIONARY[Nn]="NewNaiveBehavior"
	HONEST_DICTIONARY[s]="ScepticalBehavior"
	HONEST_DICTIONARY[Ns]="NewScepticalBehavior"
	HONEST_DICTIONARY[r]="ReputationRankingBehavior"
	HONEST_DICTIONARY[v]="ScepticalReputationBehavior"
	HONEST_DICTIONARY[Nv]="NewScepticalReputationBehavior"
	HONEST_DICTIONARY[t]="WealthThresholdBehavior"
	HONEST_DICTIONARY[w]="WealthWeightedBehavior"

declare -A DISHONEST_DICTIONARY
	DISHONEST_DICTIONARY[n]="SaboteurBehavior"
	DISHONEST_DICTIONARY[Nn]="NewSaboteurBehavior"
	DISHONEST_DICTIONARY[s]="ScaboteurBehavior"
	DISHONEST_DICTIONARY[Ns]="NewScaboteurBehavior"
	DISHONEST_DICTIONARY[r]="SaboteurReputationRankingBehavior"
	DISHONEST_DICTIONARY[v]="SaboteurScepticalReputationBehavior"
	DISHONEST_DICTIONARY[Nv]="NewSaboteurScepticalReputationBehavior"
	DISHONEST_DICTIONARY[t]="SaboteurWealthThresholdBehavior"
	DISHONEST_DICTIONARY[w]="SaboteurWealthWeightedBehavior"

HONEST_TEMPLATE='{\n\t\t"class": "HONEST_CLASS",\n\t\t"population_size": HONEST_POPULATION,\n\t\t"parameters": {\n\t\t\tHONEST_PARAMS\n\t\t\t}\n\t\t}'
DISHONEST_TEMPLATE='{\n\t\t"class": "DISHONEST_CLASS",\n\t\t"population_size": DISHONEST_POPULATION,\n\t\t"parameters": {\n\t\t\tDISHONEST_PARAMS\n\t\t\t}\n\t\t}'
BEHAVIOUR_TEMPLATE="${HONEST_TEMPLATE},\n\t\t${DISHONEST_TEMPLATE}"

declare -A HONEST_PARAMETERS
	HONEST_PARAMETERS[n]=""
	HONEST_PARAMETERS[Nn]=""
	HONEST_PARAMETERS[s]="\"threshold\": SCEPTICISM_THRESHOLD"
	HONEST_PARAMETERS[Ns]="\"scepticism_threshold\": SCEPTICISM_THRESHOLD"
	HONEST_PARAMETERS[r]="\"ranking_threshold\": RANKING_THRESHOLD"
	HONEST_PARAMETERS[v]="\"comparison_method\": \"COMPARISON_METHOD\",\n\t\t\t\"scaling\": SCALING,\n\t\t\t\"scepticism_threshold\": SCEPTICISM_THRESHOLD,\n\t\t\t\"weight_method\": \"WEIGHT_METHOD\""
	HONEST_PARAMETERS[Nv]="\"comparison_method\": \"COMPARISON_METHOD\",\n\t\t\t\"scaling\": SCALING,\n\t\t\t\"scepticism_threshold\": SCEPTICISM_THRESHOLD,\n\t\t\t\"weight_method\": \"WEIGHT_METHOD\""
	HONEST_PARAMETERS[w]=""
	HONEST_PARAMETERS[t]="\"comparison_method\": \"COMPARISON_METHOD\",\n\"scaling\": SCALING"

declare -A DISHONEST_PARAMETERS
	DISHONEST_PARAMETERS[n]="\"lie_angle\": DISHONEST_LIE_ANGLE"
	DISHONEST_PARAMETERS[Nn]="\"lie_angle\": DISHONEST_LIE_ANGLE"
	DISHONEST_PARAMETERS[s]="\"lie_angle\": DISHONEST_LIE_ANGLE,\n\t\t\t\"threshold\": SCEPTICISM_THRESHOLD"
	DISHONEST_PARAMETERS[Ns]="\"lie_angle\": DISHONEST_LIE_ANGLE,\n\t\t\t\"scepticism_threshold\": SCEPTICISM_THRESHOLD"
	DISHONEST_PARAMETERS[r]="\"lie_angle\": DISHONEST_LIE_ANGLE,\n\t\t\t\"ranking_threshold\": RANKING_THRESHOLD"
	DISHONEST_PARAMETERS[v]="\"lie_angle\": DISHONEST_LIE_ANGLE,\n\t\t\t\"comparison_method\": \"COMPARISON_METHOD\",\n\t\t\t\"scaling\": SCALING,\n\t\t\t\"scepticism_threshold\": SCEPTICISM_THRESHOLD,\n\t\t\t\"weight_method\": \"WEIGHT_METHOD\""
	DISHONEST_PARAMETERS[Nv]="\"lie_angle\": DISHONEST_LIE_ANGLE,\n\t\t\t\"comparison_method\": \"COMPARISON_METHOD\",\n\t\t\t\"scaling\": SCALING,\n\t\t\t\"scepticism_threshold\": SCEPTICISM_THRESHOLD,\n\t\t\t\"weight_method\": \"WEIGHT_METHOD\""
	DISHONEST_PARAMETERS[w]="\"lie_angle\": DISHONEST_LIE_ANGLE"
	DISHONEST_PARAMETERS[t]="\"lie_angle\": DISHONEST_LIE_ANGLE,\n\t\t\t\"comparison_method\": \"COMPARISON_METHOD\",\n\"scaling\": SCALING"

declare -A BEHAVIOR_INITIALS
	BEHAVIOR_INITIALS[n]="n"
	BEHAVIOR_INITIALS[Nn]="Nn"
	BEHAVIOR_INITIALS[s]="s"
	BEHAVIOR_INITIALS[Ns]="Ns"
	BEHAVIOR_INITIALS[r]="r"
	BEHAVIOR_INITIALS[v]="v"
	BEHAVIOR_INITIALS[Nv]="Nv"
	BEHAVIOR_INITIALS[t]="t"
	BEHAVIOR_INITIALS[w]="w"

declare -A SUB_DIR_BEHAVIOR
	SUB_DIR_BEHAVIOR[n]="naive/"
	SUB_DIR_BEHAVIOR[Nn]="new_naive/"
	SUB_DIR_BEHAVIOR[s]="sceptical/"
	SUB_DIR_BEHAVIOR[Ns]="new_sceptical/"
	SUB_DIR_BEHAVIOR[r]="ranking/"
	SUB_DIR_BEHAVIOR[v]="variable_scepticism/"
	SUB_DIR_BEHAVIOR[Nv]="variable_scepticism/"
	SUB_DIR_BEHAVIOR[t]="wealth_threshold/"
	SUB_DIR_BEHAVIOR[w]="wealth_weighted/"

declare -A BEHAVIOUR_FILENAME_ADDITIONAL_INFO
	BEHAVIOUR_FILENAME_ADDITIONAL_INFO[n]=""
	BEHAVIOUR_FILENAME_ADDITIONAL_INFO[Nn]=""
	BEHAVIOUR_FILENAME_ADDITIONAL_INFO[s]="_SCEPTICISM_THRESHOLDST"
	BEHAVIOUR_FILENAME_ADDITIONAL_INFO[Ns]="_SCEPTICISM_THRESHOLDSY"
	BEHAVIOUR_FILENAME_ADDITIONAL_INFO[r]="_RANKING_THRESHOLDRT"
	BEHAVIOUR_FILENAME_ADDITIONAL_INFO[v]="_COMPARISON_METHODCM_SCALINGSC_SCEPTICISM_THRESHOLDST_WEIGHT_METHODWM"
	BEHAVIOUR_FILENAME_ADDITIONAL_INFO[Nv]="_COMPARISON_METHODCM_SCALINGSC_SCEPTICISM_THRESHOLDST_WEIGHT_METHODWM"
	BEHAVIOUR_FILENAME_ADDITIONAL_INFO[t]="_COMPARISON_METHODCM_SCALINGSC"
	BEHAVIOUR_FILENAME_ADDITIONAL_INFO[w]=""

# payment system
declare -A PAYMENT_SYSTEM_NAME
	PAYMENT_SYSTEM_NAME[OutlierPenalisationPaymentSystem]="P"
	PAYMENT_SYSTEM_NAME[DelayedPaymentPaymentSystem]="NP"


# agents' noise
AGENT_UNIFORM_NOISE_PARAMETERS_TEMPLATE="{\n\t\t\t\t\"dishonest_noise_performance\": \"AGENT_DISHONEST_PERFORMANCE\",\n\t\t\t\t\"noise_mu\":AGENT_NOISE_MU,\n\t\t\t\t\"noise_range\": AGENT_NOISE_RANGE\n\t\t\t}"
AGENT_BIMODAL_NOISE_PARAMETERS_TEMPLATE="{\n\t\t\t\t\"noise_sampling_mu\": AGENT_NOISE_SAMPLING_MU,\n\t\t\t\t\"noise_sampling_sigma\": AGENT_NOISE_SAMPLING_SIGMA,\n\t\t\t\t\"noise_sd\": AGENT_NOISE_SD\n\t\t}"

declare -A NOISE_FILENAME_ADDITIONAL_INFO
	NOISE_FILENAME_ADDITIONAL_INFO[bimodal]="_AGENT_NOISE_SAMPLING_MUSMU_AGENT_NOISE_SAMPLING_SIGMASSD_AGENT_NOISE_SDNSD"
	NOISE_FILENAME_ADDITIONAL_INFO[average]="_AGENT_NOISE_MUNMU_AGENT_NOISE_RANGENRANG_avgSAB"
	NOISE_FILENAME_ADDITIONAL_INFO[perfect]="_AGENT_NOISE_MUNMU_AGENT_NOISE_RANGENRANG_perfSAB"



#SUMMARY #########################################################################

#Create the summary that will be used for plotting
# sed -e "s|STANDARD_DEVIATION_VALUES|${DEVIATION_VALUES_SUMMARY}|" \
# 	-e "s|DIFFICULTY_VALUES|${DIFFICULTY_VALUES_SUMMARY}|" \
# 	-e "s|NUMBER_OF_OPINIONS|${NUMBER_OF_OPINIONS_LIST}|" \
# 	-e "s|NUMBER_OF_AGENTS|${NUMBER_OF_AGENTS_SUMMARY}|" \
# 	-e "s|NUMBER_OF_STEPS|${NUM_STEP}|" \
# 	-e "s|NUMBER_OF_SIMULATIONS|${NUM_SIMULATION}|" \
# 	-e "s|COLORS|${COLORS}|" \
# 	-e "s|COMPOSITION_LIST|${COMPOSITION_LIST}|" \
# 	-e "s|NUMBER_OF_COLUMNS|${NUMBER_OF_COLUMNS}|" \
# 	-e "s|NUMBER_OF_ROWS|${NUMBER_OF_ROWS}|" \
# 	-e "s|PLOT_DIRECTORY|${PLOT_DIRECTORY}|" \
# 	-e "s|PLOT_SINGLE_RESULTS|${PLOT_SINGLE_RESULTS}|" \
# 	-e "s|TEST_NAME_LIST|${TEST_NAME_LIST}|" \
# 		${SUMMARY_TEMPLATE} > ${CONF_FILE_SUMMARY}

COUNT=0

#CONFIG FILE GENERATION ##	#######################################################################
#TODO GIOVANNI's SUGGESTION: avoid copy-paste, to avoid debug when adding new stuff
#TODO make a function call in the inner part
for AGENT_NOISE_ASSIGNATION in ${AGENT_NOISE_ASSIGNATION_LIST[*]} ; do
	#---------------- RANDOM NOISE EXPERIMENTS ----------------#
	if [[ $AGENT_NOISE_ASSIGNATION == "bimodal" ]]; then
		AGENT_NOISE_CLASS="BimodalNoise"
		AGENT_NOISE_PARAMETERS=$AGENT_BIMODAL_NOISE_PARAMETERS_TEMPLATE
		for AGENT_NOISE_SAMPLING_MU in ${AGENT_NOISE_SAMPLING_MU_LIST[*]} ; do
		for AGENT_NOISE_SAMPLING_SIGMA in ${AGENT_NOISE_SAMPLING_SIGMA_LIST[*]} ; do
		for AGENT_NOISE_SD in ${AGENT_NOISE_SD_LIST[*]} ; do
			for BEHAVIOR in ${BEHAVIOR_LIST[*]} ; do
				for HONEST_POPULATION in ${HONEST_POPULATION_LIST[*]} ; do
					DISHONEST_POPULATION=$((NUMBER_OF_ROBOTS-HONEST_POPULATION))
					for PAYMENT_SYSTEM_CLASS in ${PAYMENT_SYSTEM_CLASS_LIST[*]} ; do
						for DISHONEST_LIE_ANGLE in ${DISHONEST_LIE_ANGLES[*]} ; do
							HONEST_CLASS=${HONEST_DICTIONARY[${BEHAVIOR}]}
							DISHONEST_CLASS=${DISHONEST_DICTIONARY[${BEHAVIOR}]}
							HONEST_PARAMS=${HONEST_PARAMETERS[${BEHAVIOR}]}
							DISHONEST_PARAMS=${DISHONEST_PARAMETERS[${BEHAVIOR}]}
							FILENAME_ADDITIONAL_INFO=${BEHAVIOUR_FILENAME_ADDITIONAL_INFO[${BEHAVIOR}]}${NOISE_FILENAME_ADDITIONAL_INFO[${AGENT_NOISE_ASSIGNATION}]}
							SUB_DIR=${SUB_DIR_BEHAVIOR[${BEHAVIOR}]}
							DATA_OUTPUT_DIRECTORY="${DATA_DIR}${SUB_DIR}"
							CONFIG_OUTPUT_DIRECTORY="${CONFIG_DIR}${SUB_DIR}"
							if [[ ${DISHONEST_POPULATION} -eq 0 ]]; then
								FILENAME_BASE="${HONEST_POPULATION}${BEHAVIOR_INITIALS[${BEHAVIOR}]}_${PAYMENT_SYSTEM_NAME[${PAYMENT_SYSTEM_CLASS}]}_0LIA"
							else
								FILENAME_BASE="${HONEST_POPULATION}${BEHAVIOR_INITIALS[${BEHAVIOR}]}_${PAYMENT_SYSTEM_NAME[${PAYMENT_SYSTEM_CLASS}]}_${DISHONEST_LIE_ANGLE}LIA"
							fi
							FILENAME="${FILENAME_BASE}${FILENAME_ADDITIONAL_INFO}"
							DATA_FILENAME="${FILENAME}"
							TEMP_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}temp.json"

							mkdir -p ${CONFIG_OUTPUT_DIRECTORY}

							sed -e "s|DATA_FILENAME|${DATA_FILENAME}.csv|" \
								-e "s|WIDTH|${WIDTH}|" \
								-e "s|HEIGHT|${HEIGHT}|" \
								-e "s|FOOD_X|${FOOD_X}|" \
								-e "s|FOOD_Y|${FOOD_Y}|" \
								-e "s|FOOD_RADIUS|${FOOD_RADIUS}|" \
								-e "s|NEST_X|${NEST_X}|" \
								-e "s|NEST_Y|${NEST_Y}|" \
								-e "s|NEST_RADIUS|${NEST_RADIUS}|" \
								-e "s|SIMULATION_STEPS|${SIMULATION_STEPS}|" \
								-e "s|SIMULATION_SEED|${SIMULATION_SEED}|" \
								-e "s|NUMBER_RUNS|${NUMBER_RUNS}|" \
								-e "s|VISUALISATION_ACTIVATE|${VISUALISATION_ACTIVATE}|" \
								-e "s|VISUALISATION_FPS|${VISUALISATION_FPS}|" \
								-e "s|RANDOM_WALK_FACTOR|${RANDOM_WALK_FACTOR}|" \
								-e "s|RANDOM_WALK_LEVI_FACTOR|${RANDOM_WALK_LEVI_FACTOR}|" \
								-e "s|AGENT_RADIUS|${AGENT_RADIUS}|" \
								-e "s|AGENT_SPEED|${AGENT_SPEED}|" \
								-e "s|AGENT_COMMUNICATION_RADIUS|${AGENT_COMMUNICATION_RADIUS}|" \
								-e "s|AGENT_COMMUNICATION_STOP_TIME|${AGENT_COMMUNICATION_STOP_TIME}|" \
								-e "s|AGENT_COMMUNICATION_COOLDOWN|${AGENT_COMMUNICATION_COOLDOWN}|" \
								-e "s|AGENT_NOISE_CLASS|${AGENT_NOISE_CLASS}|" \
								-e "s|AGENT_NOISE_PARAMETERS|${AGENT_NOISE_PARAMETERS}|" \
								-e "s|AGENT_NOISE_SAMPLING_MU|${AGENT_NOISE_SAMPLING_MU}|" \
								-e "s|AGENT_NOISE_SAMPLING_SIGMA|${AGENT_NOISE_SAMPLING_SIGMA}|" \
								-e "s|AGENT_NOISE_SD|${AGENT_NOISE_SD}|" \
								-e "s|AGENT_FUEL_COST|${AGENT_FUEL_COST}|" \
								-e "s|BEHAVIOURS|${BEHAVIOUR_TEMPLATE}|" \
								-e "s|DISHONEST_CLASS|${DISHONEST_CLASS}|" \
								-e "s|HONEST_CLASS|${HONEST_CLASS}|" \
								-e "s|DISHONEST_POPULATION|${DISHONEST_POPULATION}|" \
								-e "s|HONEST_POPULATION|${HONEST_POPULATION}|" \
								-e "s|DISHONEST_PARAMS|${DISHONEST_PARAMS}|" \
								-e "s|HONEST_PARAMS|${HONEST_PARAMS}|" \
								-e "s|DISHONEST_LIE_ANGLE|${DISHONEST_LIE_ANGLE}|" \
								-e "s|PAYMENT_SYSTEM_CLASS|${PAYMENT_SYSTEM_CLASS}|" \
								-e "s|PAYMENT_SYSTEM_INITIAL_REWARD|${PAYMENT_SYSTEM_INITIAL_REWARD}|" \
								-e "s|PAYMENT_SYSTEM_INFORAMTION_SHARE|${PAYMENT_SYSTEM_INFORAMTION_SHARE}|" \
								-e "s|MARKET_CLASS|${MARKET_CLASS}|" \
								-e "s|MARKET_REWARD|${MARKET_REWARD}|" \
								-e "s|DATA_OUTPUT_DIRECTORY|${DATA_OUTPUT_DIRECTORY}|" \
								-e "s|DATA_PRECISE_RECORDING_INTERVAL|${DATA_PRECISE_RECORDING_INTERVAL}|" \
								-e "s|DATA_TRANSACTIONS_LOG|${DATA_TRANSACTIONS_LOG}|" \
									${CONFIG_FILE_TEMPLATE} > ${TEMP_CONFIG_FILENAME}

							DATA_FILENAME=$( echo ${DATA_FILENAME} | 
							 				sed -e "s|AGENT_NOISE_SAMPLING_MU|${AGENT_NOISE_SAMPLING_MU}|"\
							 				-e "s|AGENT_NOISE_SAMPLING_SIGMA|${AGENT_NOISE_SAMPLING_SIGMA}|"\
							 				-e "s|AGENT_NOISE_SD|${AGENT_NOISE_SD}|" )
							
							# 	BEHAVIOUR PARAMS_SUBSTITUTION
							if [[ ${BEHAVIOR} == "n" ]] || [[ ${BEHAVIOR} == "Nn" ]] || [[ ${BEHAVIOR} == "w" ]]; then
								CURRENT_DATA_FILENAME=$( echo ${DATA_FILENAME} | 
											sed -e "s|[\.]||g" )
								FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}${CURRENT_DATA_FILENAME}.json"
								cp ${TEMP_CONFIG_FILENAME} ${FINAL_CONFIG_FILENAME}
							else
								if [[ ${BEHAVIOR} == "s" ]] || [[ ${BEHAVIOR} == "Ns" ]]; then
									for SCEPTICISM_THRESHOLD in ${sSCEPTICISM_THRESHOLD_LIST[*]} ; do
										CURRENT_DATA_FILENAME=$( echo ${DATA_FILENAME} | 
													sed -e "s|SCEPTICISM_THRESHOLD|${SCEPTICISM_THRESHOLD}|"  \
																-e "s|[\.]||g")
										FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}${CURRENT_DATA_FILENAME}.json"
										sed -e "s|SCEPTICISM_THRESHOLD|${SCEPTICISM_THRESHOLD}|" \
											${TEMP_CONFIG_FILENAME} > ${FINAL_CONFIG_FILENAME}
									done
								else
									if [[ ${BEHAVIOR} == "r" ]]; then
										for RANKING_THRESHOLD in ${rRANKING_THRESHOLD_LIST[*]} ; do
											CURRENT_DATA_FILENAME=$( echo ${DATA_FILENAME} | 
														sed -e "s|RANKING_THRESHOLD|${RANKING_THRESHOLD}|"  \
																-e "s|[\.]||g")
											FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}${CURRENT_DATA_FILENAME}.json"
											sed -e "s|RANKING_THRESHOLD|${RANKING_THRESHOLD}|" \
												${TEMP_CONFIG_FILENAME} > ${FINAL_CONFIG_FILENAME}
										done
									else
										if [[ ${BEHAVIOR} == "v" ]] || [[ ${BEHAVIOR} == "Nv" ]]; then
											for COMPARISON_METHOD in ${vCOMPARISON_METHOD_LIST[*]} ; do
											for SCALING in ${vSCALING_LIST[*]} ; do
											for SCEPTICISM_THRESHOLD in ${vSCEPTICISM_THRESHOLD_LIST[*]} ; do
											for WEIGHT_METHOD in ${vWEIGHT_METHOD_LIST[*]} ; do
												CURRENT_DATA_FILENAME=$( echo ${DATA_FILENAME} | 
															sed -e "s|COMPARISON_METHOD|${COMPARISON_METHOD}|" \
															-e "s|SCALING|${SCALING}|" \
															-e "s|SCEPTICISM_THRESHOLD|${SCEPTICISM_THRESHOLD}|" \
															-e "s|WEIGHT_METHOD|${WEIGHT_METHOD}|" \
																-e "s|[\.]||g" )
												FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}${CURRENT_DATA_FILENAME}.json"
												sed -e "s|COMPARISON_METHOD|${COMPARISON_METHOD}|" \
													-e "s|SCALING|${SCALING}|" \
													-e "s|SCEPTICISM_THRESHOLD|${SCEPTICISM_THRESHOLD}|" \
													-e "s|WEIGHT_METHOD|${WEIGHT_METHOD}|" \
													${TEMP_CONFIG_FILENAME} > ${FINAL_CONFIG_FILENAME}
											done
											done
											done
											done
										else
											if [[ ${BEHAVIOR} == "t" ]]; then
												for COMPARISON_METHOD in ${tCOMPARISON_METHOD_LIST[*]} ; do
												for SCALING in ${tSCALING_LIST[*]} ; do
													CURRENT_DATA_FILENAME=$( echo ${DATA_FILENAME} | 
																sed -e "s|COMPARISON_METHOD|${COMPARISON_METHOD}|" \
																-e "s|SCALING|${SCALING}|" \
																-e "s|[\.]||g")
													FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}${CURRENT_DATA_FILENAME}.json"
													sed -e "s|COMPARISON_METHOD|${COMPARISON_METHOD}|" \
														-e "s|SCALING|${SCALING}|" \
														${TEMP_CONFIG_FILENAME} > ${FINAL_CONFIG_FILENAME}
												done
												done
											fi
										fi
									fi
								fi
							fi
							COUNT=$((COUNT + 1))
							rm ${TEMP_CONFIG_FILENAME}
						done
					done
				done
			done
		done
		done
		done
	else #------------------- FIXED NOISE EXPERIMENTS -------------------#
		AGENT_NOISE_CLASS="UniformNoise"
		AGENT_NOISE_PARAMETERS=$AGENT_UNIFORM_NOISE_PARAMETERS_TEMPLATE
		for AGENT_NOISE_MU in ${AGENT_NOISE_MU_LIST[*]} ; do
		for AGENT_NOISE_RANGE in ${AGENT_NOISE_RANGE_LIST[*]} ; do
			for BEHAVIOR in ${BEHAVIOR_LIST[*]} ; do
				for HONEST_POPULATION in ${HONEST_POPULATION_LIST[*]} ; do
					DISHONEST_POPULATION=$((NUMBER_OF_ROBOTS-HONEST_POPULATION))
					for PAYMENT_SYSTEM_CLASS in ${PAYMENT_SYSTEM_CLASS_LIST[*]} ; do
						for DISHONEST_LIE_ANGLE in ${DISHONEST_LIE_ANGLES[*]} ; do
							HONEST_CLASS=${HONEST_DICTIONARY[${BEHAVIOR}]}
							DISHONEST_CLASS=${DISHONEST_DICTIONARY[${BEHAVIOR}]}
							HONEST_PARAMS=${HONEST_PARAMETERS[${BEHAVIOR}]}
							DISHONEST_PARAMS=${DISHONEST_PARAMETERS[${BEHAVIOR}]}
							FILENAME_ADDITIONAL_INFO=${BEHAVIOUR_FILENAME_ADDITIONAL_INFO[${BEHAVIOR}]}
							SUB_DIR=${SUB_DIR_BEHAVIOR[${BEHAVIOR}]}
							DATA_OUTPUT_DIRECTORY="${DATA_DIR}${SUB_DIR}"
							CONFIG_OUTPUT_DIRECTORY="${CONFIG_DIR}${SUB_DIR}"
							if [[ ${DISHONEST_POPULATION} -eq 0 ]]; then
								FILENAME_BASE="${HONEST_POPULATION}${BEHAVIOR_INITIALS[${BEHAVIOR}]}_${PAYMENT_SYSTEM_NAME[${PAYMENT_SYSTEM_CLASS}]}_0LIA"
							else
								FILENAME_BASE="${HONEST_POPULATION}${BEHAVIOR_INITIALS[${BEHAVIOR}]}_${PAYMENT_SYSTEM_NAME[${PAYMENT_SYSTEM_CLASS}]}_${DISHONEST_LIE_ANGLE}LIA"
							fi
							FILENAME="${FILENAME_BASE}${FILENAME_ADDITIONAL_INFO}${NOISE_FILENAME_ADDITIONAL_INFO[${AGENT_NOISE_ASSIGNATION}]}"
							DATA_FILENAME="${FILENAME}"
							TEMP_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}temp.json"

							mkdir -p ${CONFIG_OUTPUT_DIRECTORY}

							sed -e "s|DATA_FILENAME|${DATA_FILENAME}.csv|" \
								-e "s|WIDTH|${WIDTH}|" \
								-e "s|HEIGHT|${HEIGHT}|" \
								-e "s|FOOD_X|${FOOD_X}|" \
								-e "s|FOOD_Y|${FOOD_Y}|" \
								-e "s|FOOD_RADIUS|${FOOD_RADIUS}|" \
								-e "s|NEST_X|${NEST_X}|" \
								-e "s|NEST_Y|${NEST_Y}|" \
								-e "s|NEST_RADIUS|${NEST_RADIUS}|" \
								-e "s|SIMULATION_STEPS|${SIMULATION_STEPS}|" \
								-e "s|SIMULATION_SEED|${SIMULATION_SEED}|" \
								-e "s|NUMBER_RUNS|${NUMBER_RUNS}|" \
								-e "s|VISUALISATION_ACTIVATE|${VISUALISATION_ACTIVATE}|" \
								-e "s|VISUALISATION_FPS|${VISUALISATION_FPS}|" \
								-e "s|RANDOM_WALK_FACTOR|${RANDOM_WALK_FACTOR}|" \
								-e "s|RANDOM_WALK_LEVI_FACTOR|${RANDOM_WALK_LEVI_FACTOR}|" \
								-e "s|AGENT_RADIUS|${AGENT_RADIUS}|" \
								-e "s|AGENT_SPEED|${AGENT_SPEED}|" \
								-e "s|AGENT_COMMUNICATION_RADIUS|${AGENT_COMMUNICATION_RADIUS}|" \
								-e "s|AGENT_COMMUNICATION_STOP_TIME|${AGENT_COMMUNICATION_STOP_TIME}|" \
								-e "s|AGENT_COMMUNICATION_COOLDOWN|${AGENT_COMMUNICATION_COOLDOWN}|" \
								-e "s|AGENT_NOISE_CLASS|${AGENT_NOISE_CLASS}|" \
								-e "s|AGENT_NOISE_PARAMETERS|${AGENT_NOISE_PARAMETERS}|" \
								-e "s|AGENT_DISHONEST_PERFORMANCE|${AGENT_NOISE_ASSIGNATION}|" \
								-e "s|AGENT_NOISE_MU|${AGENT_NOISE_MU}|" \
								-e "s|AGENT_NOISE_RANGE|${AGENT_NOISE_RANGE}|" \
								-e "s|AGENT_FUEL_COST|${AGENT_FUEL_COST}|" \
								-e "s|BEHAVIOURS|${BEHAVIOUR_TEMPLATE}|" \
								-e "s|DISHONEST_CLASS|${DISHONEST_CLASS}|" \
								-e "s|HONEST_CLASS|${HONEST_CLASS}|" \
								-e "s|DISHONEST_POPULATION|${DISHONEST_POPULATION}|" \
								-e "s|HONEST_POPULATION|${HONEST_POPULATION}|" \
								-e "s|DISHONEST_PARAMS|${DISHONEST_PARAMS}|" \
								-e "s|HONEST_PARAMS|${HONEST_PARAMS}|" \
								-e "s|DISHONEST_LIE_ANGLE|${DISHONEST_LIE_ANGLE}|" \
								-e "s|PAYMENT_SYSTEM_CLASS|${PAYMENT_SYSTEM_CLASS}|" \
								-e "s|PAYMENT_SYSTEM_INITIAL_REWARD|${PAYMENT_SYSTEM_INITIAL_REWARD}|" \
								-e "s|PAYMENT_SYSTEM_INFORAMTION_SHARE|${PAYMENT_SYSTEM_INFORAMTION_SHARE}|" \
								-e "s|MARKET_CLASS|${MARKET_CLASS}|" \
								-e "s|MARKET_REWARD|${MARKET_REWARD}|" \
								-e "s|DATA_OUTPUT_DIRECTORY|${DATA_OUTPUT_DIRECTORY}|" \
								-e "s|DATA_PRECISE_RECORDING_INTERVAL|${DATA_PRECISE_RECORDING_INTERVAL}|" \
								-e "s|DATA_TRANSACTIONS_LOG|${DATA_TRANSACTIONS_LOG}|" \
									${CONFIG_FILE_TEMPLATE} > ${TEMP_CONFIG_FILENAME}

								DATA_FILENAME=$( echo ${DATA_FILENAME} | 
							 				sed -e "s|AGENT_NOISE_MU|${AGENT_NOISE_MU}|"\
							 				-e "s|AGENT_NOISE_RANGE|${AGENT_NOISE_RANGE}|" )
							
							# 	BEHAVIOUR PARAMS_SUBSTITUTION
							if [[ ${BEHAVIOR} == "n" ]] || [[ ${BEHAVIOR} == "Nn" ]] || [[ ${BEHAVIOR} == "w" ]]; then
								# FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}${DATA_FILENAME}.json"
								CURRENT_DATA_FILENAME=$( echo ${DATA_FILENAME} | 
											sed -e "s|[\.]||g" )
								FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}${CURRENT_DATA_FILENAME}.json"
								cp ${TEMP_CONFIG_FILENAME} ${FINAL_CONFIG_FILENAME}
							else
								if [[ ${BEHAVIOR} == "s" ]] || [[ ${BEHAVIOR} == "Ns" ]]; then
									for SCEPTICISM_THRESHOLD in ${sSCEPTICISM_THRESHOLD_LIST[*]} ; do
										CURRENT_DATA_FILENAME=$( echo ${DATA_FILENAME} | 
													sed -e "s|SCEPTICISM_THRESHOLD|${SCEPTICISM_THRESHOLD}|"  \
																-e "s|[\.]||g")
										FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}${CURRENT_DATA_FILENAME}.json"
										sed -e "s|SCEPTICISM_THRESHOLD|${SCEPTICISM_THRESHOLD}|" \
											${TEMP_CONFIG_FILENAME} > ${FINAL_CONFIG_FILENAME}
									done
								else
									if [[ ${BEHAVIOR} == "r" ]]; then
										for RANKING_THRESHOLD in ${rRANKING_THRESHOLD_LIST[*]} ; do
											CURRENT_DATA_FILENAME=$( echo ${DATA_FILENAME} | 
														sed -e "s|RANKING_THRESHOLD|${RANKING_THRESHOLD}|"  \
																-e "s|[\.]||g")
											FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}${CURRENT_DATA_FILENAME}.json"
											sed -e "s|RANKING_THRESHOLD|${RANKING_THRESHOLD}|" \
												${TEMP_CONFIG_FILENAME} > ${FINAL_CONFIG_FILENAME}
										done
									else
										if [[ ${BEHAVIOR} == "v" ]] || [[ ${BEHAVIOR} == "Nv" ]]; then
											for COMPARISON_METHOD in ${vCOMPARISON_METHOD_LIST[*]} ; do
											for SCALING in ${vSCALING_LIST[*]} ; do
											for SCEPTICISM_THRESHOLD in ${vSCEPTICISM_THRESHOLD_LIST[*]} ; do
											for WEIGHT_METHOD in ${vWEIGHT_METHOD_LIST[*]} ; do
												CURRENT_DATA_FILENAME=$( echo ${DATA_FILENAME} | 
															sed -e "s|COMPARISON_METHOD|${COMPARISON_METHOD}|" \
															-e "s|SCALING|${SCALING}|" \
															-e "s|SCEPTICISM_THRESHOLD|${SCEPTICISM_THRESHOLD}|" \
															-e "s|WEIGHT_METHOD|${WEIGHT_METHOD}|" \
																-e "s|[\.]||g" )
												FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}${CURRENT_DATA_FILENAME}.json"
												sed -e "s|COMPARISON_METHOD|${COMPARISON_METHOD}|" \
													-e "s|SCALING|${SCALING}|" \
													-e "s|SCEPTICISM_THRESHOLD|${SCEPTICISM_THRESHOLD}|" \
													-e "s|WEIGHT_METHOD|${WEIGHT_METHOD}|" \
													${TEMP_CONFIG_FILENAME} > ${FINAL_CONFIG_FILENAME}
											done
											done
											done
											done
										else
											if [[ ${BEHAVIOR} == "t" ]]; then
												for COMPARISON_METHOD in ${tCOMPARISON_METHOD_LIST[*]} ; do
												for SCALING in ${tSCALING_LIST[*]} ; do
													CURRENT_DATA_FILENAME=$( echo ${DATA_FILENAME} | 
																sed -e "s|COMPARISON_METHOD|${COMPARISON_METHOD}|" \
																-e "s|SCALING|${SCALING}|" \
																-e "s|[\.]||g" )
													FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}${CURRENT_DATA_FILENAME}.json"
													sed -e "s|COMPARISON_METHOD|${COMPARISON_METHOD}|" \
														-e "s|SCALING|${SCALING}|" \
														${TEMP_CONFIG_FILENAME} > ${FINAL_CONFIG_FILENAME}
												done
												done
											fi
										fi
									fi
								fi
							fi
							COUNT=$((COUNT + 1))
							rm ${TEMP_CONFIG_FILENAME}
							COUNT=$((COUNT + 1))
						done
					done
				done
			done
		done
		done
	fi
done

echo "CREATED " $COUNT " CONFIGURATIONS"
