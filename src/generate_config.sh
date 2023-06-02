#!/bin/bash

# automatically generates multiple config file for the information market simulation
# all the permitted (wrt behaviour.py) combinations of parameters are generated
# the generated config files are stored in the CONFIG_DIR directory
# config files are named according to the parameters they contain
# filename of results of configurations runs are identical to the config file name
# OPTIONALLY, can pass a parameter to create a subdirectory in the data directory
#             for the current experiment
#
# usage: ./generate_config.sh [experiment_subdirectory_name]

#NOTE -- ATTENTION: IF YOU MOVE THE FILE generate_config.sh, YOU MUST UPDATE THE FOLLOWING LINES
PROJECT_HOME=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )/..
CONFIG_DIR="${PROJECT_HOME}/config"
ASSETS_DIR="${PROJECT_HOME}/assets"
EXEC_FILE="${PROJECT_HOME}/src/info_market.py"
DATA_DIR="${PROJECT_HOME}/data"
if [ $# -ne 0 ]; then
  DATA_DIR="${DATA_DIR}/$1"
fi

CONFIG_FILE_TEMPLATE="${ASSETS_DIR}/config_template"


#########################################################################
# --- PLEASE REFER TO README FOR MORE INFORMATION ON THE PARAMETERS --- #
#########################################################################


#GENERAL PARAMETERS ####################################################
# - DO NOT MODIFY,  UNLESS YOU WANT TO INTRODUCE ENVIRONMENT CHANGES - #

#environment, food, nest, visualisation, random walk, agent, payment system, market

. ./fixed_params_generate_config.sh

############################################################################################
############################################################################################
############################################################################################
#EXPERIMENT PARAMETERS: MODIFY AS YOU WILL #################################################
# ----------------- NOTE LISTS MUST BE IN THIS FORMAT: (value1 ... valueN) --------------- #
# ----------------- NOTE BOOLs = {true, false} ------------------------------------------- #

#simulation, visualisation, noise, combine_strategy, payment system, data collection, robots, behaviors

. ./params_experiment_generate_config.sh

# PARAMETERS DICTIONARIES #######################################################
# ----------------- DO NOT MODIFY, UNLESS YOU MODIFY behaviour.py ------------- #

# behavior
declare -A HONEST_DICTIONARY
	HONEST_DICTIONARY[b]="BenchmarkBehavior"
	HONEST_DICTIONARY[n]="NaiveBehavior"
	HONEST_DICTIONARY[Nn]="NewNaiveBehavior"
	HONEST_DICTIONARY[s]="ScepticalBehavior"
	HONEST_DICTIONARY[Ns]="NewScepticalBehavior"
	HONEST_DICTIONARY[r]="ReputationRankingBehavior"
	HONEST_DICTIONARY[v]="VariableScepticalBehavior"
	HONEST_DICTIONARY[Nv]="NewVariableScepticalBehavior"
	HONEST_DICTIONARY[t]="WealthThresholdBehavior"
	HONEST_DICTIONARY[w]="WealthWeightedBehavior"
	HONEST_DICTIONARY[h]="ReputationHistoryBehavior"
	HONEST_DICTIONARY[hs]="ReputationHistoryScepticalBehavior"
	HONEST_DICTIONARY[c]="CapitalistBehavior"


declare -A DISHONEST_DICTIONARY
	DISHONEST_DICTIONARY[b]="SaboteurBenchmarkBehavior"
	DISHONEST_DICTIONARY[n]="SaboteurBehavior"
	DISHONEST_DICTIONARY[Nn]="NewSaboteurBehavior"
	DISHONEST_DICTIONARY[s]="ScaboteurBehavior"
	DISHONEST_DICTIONARY[Ns]="NewScaboteurBehavior"
	DISHONEST_DICTIONARY[r]="SaboteurReputationRankingBehavior"
	DISHONEST_DICTIONARY[v]="SaboteurVariableScepticalBehavior"
	DISHONEST_DICTIONARY[Nv]="NewSaboteurVariableScepticalBehavior"
	DISHONEST_DICTIONARY[t]="SaboteurWealthThresholdBehavior"
	DISHONEST_DICTIONARY[w]="SaboteurWealthWeightedBehavior"
	DISHONEST_DICTIONARY[h]="SaboteurReputationHistoryBehavior"
	DISHONEST_DICTIONARY[hs]=Saboteur"ReputationHistoryScepticalBehavior"
	DISHONEST_DICTIONARY[c]="SaboteurCapitalistBehavior"

HONEST_TEMPLATE='{\n\t\t"class": "HONEST_CLASS",\n\t\t"population_size": HONEST_POPULATION,\n\t\t"parameters": {\n\t\t\tHONEST_PARAMS\n\t\t\t}\n\t\t}'
DISHONEST_TEMPLATE='{\n\t\t"class": "DISHONEST_CLASS",\n\t\t"population_size": DISHONEST_POPULATION,\n\t\t"parameters": {\n\t\t\tDISHONEST_PARAMS\n\t\t\t}\n\t\t}'
BEHAVIOUR_TEMPLATE="${HONEST_TEMPLATE},\n\t\t${DISHONEST_TEMPLATE}"

declare -A HONEST_PARAMETERS
	HONEST_PARAMETERS[b]="\"number_of_robots\":HONEST_POPULATION,\n\t\t\t\"number_of_byzantines\":DISHONEST_POPULATION,\n\t\t\t\"byzantine_performance\":\"AGENT_NOISE_ASSIGNATION\",\n\t\t\t\"good_acceptance_rate\": GOOD_ACCEPTANCE_RATE,\n\t\t\t\"bad_acceptance_rate\": BAD_ACCEPTANCE_RATE,\n\t\t\t\"saboteur_acceptance_rate\": SABOTEUR_ACCEPTANCE_RATE"
	HONEST_PARAMETERS[n]=""
	HONEST_PARAMETERS[Nn]=""
	HONEST_PARAMETERS[s]="\"threshold\": SCEPTICISM_THRESHOLD"
	HONEST_PARAMETERS[Ns]="\"scepticism_threshold\": SCEPTICISM_THRESHOLD"
	HONEST_PARAMETERS[r]="\"ranking_threshold\": RANKING_THRESHOLD,\n\t\t\t\"reputation_method\": \"REPUTATION_METHOD\""
	HONEST_PARAMETERS[v]="\"comparison_method\": \"COMPARISON_METHOD\",\n\t\t\t\"scaling\": SCALING,\n\t\t\t\"scepticism_threshold\": SCEPTICISM_THRESHOLD,\n\t\t\t\"weight_method\": \"WEIGHT_METHOD\""
	HONEST_PARAMETERS[Nv]="\"comparison_method\": \"COMPARISON_METHOD\",\n\t\t\t\"scaling\": SCALING,\n\t\t\t\"scepticism_threshold\": SCEPTICISM_THRESHOLD,\n\t\t\t\"weight_method\": \"WEIGHT_METHOD\""
	HONEST_PARAMETERS[w]=""
	HONEST_PARAMETERS[t]="\"comparison_method\": \"COMPARISON_METHOD\",\n\t\t\t\"scaling\": SCALING,\n\t\t\t\"reputation_method\": \"REPUTATION_METHOD\""
	HONEST_PARAMETERS[h]="\"verification_method\": \"VERIFICATION_METHOD\",\n\t\t\t\"threshold_method\": \"THRESHOLD_METHOD\",\n\t\t\t\"scaling\": SCALING,\n\t\t\t\"kd\": KDIFF,\n\t\t\t\"reputation_method\": \"REPUTATION_METHOD\""
	HONEST_PARAMETERS[hs]="\"verification_method\": \"VERIFICATION_METHOD\",\n\t\t\t\"threshold_method\": \"THRESHOLD_METHOD\",\n\t\t\t\"scaling\": SCALING,\n\t\t\t\"kd\": KDIFF,\n\t\t\t\"scepticism_threshold\": SCEPTICISM_THRESHOLD"
	HONEST_PARAMETERS[c]="\"reputation_method\": \"REPUTATION_METHOD\""
	
declare -A DISHONEST_PARAMETERS
	DISHONEST_PARAMETERS[b]="\"lie_angle\": DISHONEST_LIE_ANGLE,\n\t\t\t\"number_of_robots\":HONEST_POPULATION,\n\t\t\t\"number_of_byzantines\":DISHONEST_POPULATION,\n\t\t\t\"byzantine_performance\":\"AGENT_NOISE_ASSIGNATION\",\n\t\t\t\"good_acceptance_rate\": GOOD_ACCEPTANCE_RATE,\n\t\t\t\"bad_acceptance_rate\": BAD_ACCEPTANCE_RATE,\n\t\t\t\"saboteur_acceptance_rate\": SABOTEUR_ACCEPTANCE_RATE"
	DISHONEST_PARAMETERS[n]="\"lie_angle\": DISHONEST_LIE_ANGLE"
	DISHONEST_PARAMETERS[Nn]="\"lie_angle\": DISHONEST_LIE_ANGLE"
	DISHONEST_PARAMETERS[s]="\"lie_angle\": DISHONEST_LIE_ANGLE,\n\t\t\t\"threshold\": SCEPTICISM_THRESHOLD"
	DISHONEST_PARAMETERS[Ns]="\"lie_angle\": DISHONEST_LIE_ANGLE,\n\t\t\t\"scepticism_threshold\": SCEPTICISM_THRESHOLD"
	DISHONEST_PARAMETERS[r]="\"lie_angle\": DISHONEST_LIE_ANGLE,\n\t\t\t\"ranking_threshold\": RANKING_THRESHOLD,\n\t\t\t\"reputation_method\": \"REPUTATION_METHOD\""
	DISHONEST_PARAMETERS[v]="\"lie_angle\": DISHONEST_LIE_ANGLE,\n\t\t\t\"comparison_method\": \"COMPARISON_METHOD\",\n\t\t\t\"scaling\": SCALING,\n\t\t\t\"scepticism_threshold\": SCEPTICISM_THRESHOLD,\n\t\t\t\"weight_method\": \"WEIGHT_METHOD\""
	DISHONEST_PARAMETERS[Nv]="\"lie_angle\": DISHONEST_LIE_ANGLE,\n\t\t\t\"comparison_method\": \"COMPARISON_METHOD\",\n\t\t\t\"scaling\": SCALING,\n\t\t\t\"scepticism_threshold\": SCEPTICISM_THRESHOLD,\n\t\t\t\"weight_method\": \"WEIGHT_METHOD\""
	DISHONEST_PARAMETERS[w]="\"lie_angle\": DISHONEST_LIE_ANGLE"
	DISHONEST_PARAMETERS[t]="\"lie_angle\": DISHONEST_LIE_ANGLE,\n\t\t\t\"comparison_method\": \"COMPARISON_METHOD\",\n\t\t\t\"scaling\": SCALING,\n\t\t\t\"reputation_method\": \"REPUTATION_METHOD\""
	DISHONEST_PARAMETERS[h]="\"lie_angle\": DISHONEST_LIE_ANGLE,\n\t\t\t\"verification_method\": \"VERIFICATION_METHOD\",\n\t\t\t\"threshold_method\": \"THRESHOLD_METHOD\",\n\t\t\t\"scaling\": SCALING,\n\t\t\t\"kd\": KDIFF,\n\t\t\t\"reputation_method\": \"REPUTATION_METHOD\""
	DISHONEST_PARAMETERS[hs]="\"lie_angle\": DISHONEST_LIE_ANGLE,\n\t\t\t\"verification_method\": \"VERIFICATION_METHOD\",\n\t\t\t\"threshold_method\": \"THRESHOLD_METHOD\",\n\t\t\t\"scaling\": SCALING,\n\t\t\t\"kd\": KDIFF,\n\t\t\t\"scepticism_threshold\": SCEPTICISM_THRESHOLD"
	DISHONEST_PARAMETERS[c]="\"lie_angle\": DISHONEST_LIE_ANGLE,\n\t\t\t\"reputation_method\": \"REPUTATION_METHOD\""

declare -A BEHAVIOR_INITIALS
	BEHAVIOR_INITIALS[b]="b"
	BEHAVIOR_INITIALS[n]="n"
	BEHAVIOR_INITIALS[Nn]="Nn"
	BEHAVIOR_INITIALS[s]="s"
	BEHAVIOR_INITIALS[Ns]="Ns"
	BEHAVIOR_INITIALS[r]="r"
	BEHAVIOR_INITIALS[v]="v"
	BEHAVIOR_INITIALS[Nv]="Nv"
	BEHAVIOR_INITIALS[t]="t"
	BEHAVIOR_INITIALS[w]="w"
	BEHAVIOR_INITIALS[h]="h"
	BEHAVIOR_INITIALS[hs]="hs"
	BEHAVIOR_INITIALS[c]="c"

declare -A SUB_DIR_BEHAVIOR
	SUB_DIR_BEHAVIOR[b]="benchmark"
	SUB_DIR_BEHAVIOR[n]="naive"
	SUB_DIR_BEHAVIOR[Nn]="new_naive"
	SUB_DIR_BEHAVIOR[s]="sceptical"
	SUB_DIR_BEHAVIOR[Ns]="new_sceptical"
	SUB_DIR_BEHAVIOR[r]="ranking"
	SUB_DIR_BEHAVIOR[v]="variable_scepticism"
	SUB_DIR_BEHAVIOR[Nv]="variable_scepticism"
	SUB_DIR_BEHAVIOR[t]="wealth_threshold"
	SUB_DIR_BEHAVIOR[w]="wealth_weighted"
	SUB_DIR_BEHAVIOR[h]="history"
	SUB_DIR_BEHAVIOR[hs]="history_sceptical"
	SUB_DIR_BEHAVIOR[c]="capitalist"

declare -A BEHAVIOUR_FILENAME_ADDITIONAL_INFO
	BEHAVIOUR_FILENAME_ADDITIONAL_INFO[b]="_GOOD_ACCEPTANCE_RATEGAR_BAD_ACCEPTANCE_RATEBAR_SABOTEUR_ACCEPTANCE_RATESAR"
	BEHAVIOUR_FILENAME_ADDITIONAL_INFO[n]=""
	BEHAVIOUR_FILENAME_ADDITIONAL_INFO[Nn]=""
	BEHAVIOUR_FILENAME_ADDITIONAL_INFO[s]="_SCEPTICISM_THRESHOLDST"
	BEHAVIOUR_FILENAME_ADDITIONAL_INFO[Ns]="_SCEPTICISM_THRESHOLDSY"
	BEHAVIOUR_FILENAME_ADDITIONAL_INFO[r]="_RANKING_THRESHOLDRT_REPUTATION_METHODRM"
	BEHAVIOUR_FILENAME_ADDITIONAL_INFO[v]="_COMPARISON_METHODCM_SCALINGSC_SCEPTICISM_THRESHOLDST_WEIGHT_METHODWM"
	BEHAVIOUR_FILENAME_ADDITIONAL_INFO[Nv]="_COMPARISON_METHODCM_SCALINGSC_SCEPTICISM_THRESHOLDST_WEIGHT_METHODWM"
	BEHAVIOUR_FILENAME_ADDITIONAL_INFO[t]="_COMPARISON_METHODCM_SCALINGSC_REPUTATION_METHODRM"
	BEHAVIOUR_FILENAME_ADDITIONAL_INFO[w]=""
	BEHAVIOUR_FILENAME_ADDITIONAL_INFO[h]="_VERIFICATION_METHODVM_THRESHOLD_METHODTM_SCALINGSC_KDIFFKD_REPUTATION_METHODRM"
	BEHAVIOUR_FILENAME_ADDITIONAL_INFO[hs]="_VERIFICATION_METHODVM_THRESHOLD_METHODTM_SCALINGSC_KDIFFKD_SCEPTICISM_THRESHOLDST"
	BEHAVIOUR_FILENAME_ADDITIONAL_INFO[c]="_REPUTATION_METHODRM"

# information combine strategy
declare -A COMBINE_STRATEGIES
	COMBINE_STRATEGIES[waa]="WeightedAverageAgeStrategy"
	COMBINE_STRATEGIES[wara]="WeightedAverageReputationAgeStrategy"
	COMBINE_STRATEGIES[rwar]="RunningWeightedAverageReputationStrategy"
	COMBINE_STRATEGIES[nrwar]="NewRunningWeightedAverageReputationStrategy"
	COMBINE_STRATEGIES[fwar]="FullWeightedAverageReputationStrategy"
	COMBINE_STRATEGIES[nfwar]="NewFullWeightedAverageReputationStrategy"

declare -A COMBINE_STRATEGIES_INITIALS
	COMBINE_STRATEGIES_INITIALS[waa]="waa"
	COMBINE_STRATEGIES_INITIALS[wara]="wara"
	COMBINE_STRATEGIES_INITIALS[rwar]="rwar"
	COMBINE_STRATEGIES_INITIALS[nrwar]="nrwar"
	COMBINE_STRATEGIES_INITIALS[fwar]="fwar"
	COMBINE_STRATEGIES_INITIALS[nfwar]="nfwar"


# payment system
declare -A PAYMENT_SYSTEM_NAME
	PAYMENT_SYSTEM_NAME[OutlierPenalisationPaymentSystem]="P"
	PAYMENT_SYSTEM_NAME[DelayedPaymentPaymentSystem]="NP"
	
#TODO create params for each payment system
declare -A PAYMENT_SYSTEM_PARAMETERS
	PAYMENT_SYSTEM_PARAMETERS[OutlierPenalisationPaymentSystem]="\"information_share\": INFORMATION_SHARE,\n\t\t\t\"reputation_stake\": REPUTATION_STAKE"
	PAYMENT_SYSTEM_PARAMETERS[DelayedPaymentPaymentSystem]="\"information_share\": INFORMATION_SHARE"

# declare -A PAYMENT_SYSTEM_BEHAVIOR_REPUTATION_METRIC
# 	PAYMENT_SYSTEM_BEHAVIOR_REPUTATION_METRIC[n]=""
# 	PAYMENT_SYSTEM_BEHAVIOR_REPUTATION_METRIC[s]=""
# 	PAYMENT_SYSTEM_BEHAVIOR_REPUTATION_METRIC[r]="r"
# 	PAYMENT_SYSTEM_BEHAVIOR_REPUTATION_METRIC[t]="r"
# 	PAYMENT_SYSTEM_BEHAVIOR_REPUTATION_METRIC[Nv]="r"
# 	PAYMENT_SYSTEM_BEHAVIOR_REPUTATION_METRIC[h]="h"
# 	PAYMENT_SYSTEM_BEHAVIOR_REPUTATION_METRIC[hs]="h"
	

declare -A REPUTATION_STAKING_NAME_PREFIX
	REPUTATION_STAKING_NAME_PREFIX[true]=""
	REPUTATION_STAKING_NAME_PREFIX[false]="N"


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


#CONFIG FILE GENERATION ##	#######################################################################
COUNT=0
declare -a GENERATED_FILENAMES=()
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
					for PAYMENT_SYSTEM_REPUTATION_STAKE in ${PAYMENT_SYSTEM_REPUTATION_STAKE_LIST[*]} ; do
					if ! [[ $PAYMENT_SYSTEM_REPUTATION_STAKE == "true" ]] || ! [[ $PAYMENT_SYSTEM_CLASS == "DelayedPaymentPaymentSystem" ]]; then
						for DISHONEST_LIE_ANGLE in ${DISHONEST_LIE_ANGLE_LIST[*]} ; do
							for COMBINE_STRATEGY in ${COMBINE_STRATEGY_LIST[*]} ; do
								HONEST_CLASS=${HONEST_DICTIONARY[${BEHAVIOR}]}
								DISHONEST_CLASS=${DISHONEST_DICTIONARY[${BEHAVIOR}]}
								HONEST_PARAMS=${HONEST_PARAMETERS[${BEHAVIOR}]}
								DISHONEST_PARAMS=${DISHONEST_PARAMETERS[${BEHAVIOR}]}
								COMBINE_STRATEGY_CLASS=${COMBINE_STRATEGIES[${COMBINE_STRATEGY}]}
								FILENAME_ADDITIONAL_INFO=${BEHAVIOUR_FILENAME_ADDITIONAL_INFO[${BEHAVIOR}]}${NOISE_FILENAME_ADDITIONAL_INFO[${AGENT_NOISE_ASSIGNATION}]}
								SUB_DIR=${SUB_DIR_BEHAVIOR[${BEHAVIOR}]}
								DATA_OUTPUT_DIRECTORY="${DATA_DIR}/${SUB_DIR}"
								CONFIG_OUTPUT_DIRECTORY="${CONFIG_DIR}/${SUB_DIR}"
								if [[ ${DISHONEST_POPULATION} -eq 0 ]]; then
									FILENAME_BASE="${HONEST_POPULATION}${BEHAVIOR_INITIALS[${BEHAVIOR}]}_${COMBINE_STRATEGIES_INITIALS[${COMBINE_STRATEGY}]}CS_${PAYMENT_SYSTEM_NAME[${PAYMENT_SYSTEM_CLASS}]}_${REPUTATION_STAKING_NAME_PREFIX[${PAYMENT_SYSTEM_REPUTATION_STAKE}]}RS_0LIA"
								else
									FILENAME_BASE="${HONEST_POPULATION}${BEHAVIOR_INITIALS[${BEHAVIOR}]}_${COMBINE_STRATEGIES_INITIALS[${COMBINE_STRATEGY}]}CS_${PAYMENT_SYSTEM_NAME[${PAYMENT_SYSTEM_CLASS}]}_${REPUTATION_STAKING_NAME_PREFIX[${PAYMENT_SYSTEM_REPUTATION_STAKE}]}RS_${DISHONEST_LIE_ANGLE}LIA"
								fi
								FILENAME="${FILENAME_BASE}${FILENAME_ADDITIONAL_INFO}"
								DATA_FILENAME="${FILENAME}"
								TEMP_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}/temp.json"

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
									-e "s|COMBINE_STRATEGY_CLASS|${COMBINE_STRATEGY_CLASS}|" \
									-e "s|PAYMENT_SYSTEM_CLASS|${PAYMENT_SYSTEM_CLASS}|" \
									-e "s|PAYMENT_SYSTEM_INITIAL_REWARD|${PAYMENT_SYSTEM_INITIAL_REWARD}|" \
									-e "s|PAYMENT_SYSTEM_INFORMATION_SHARE|${PAYMENT_SYSTEM_INFORMATION_SHARE}|" \
									-e "s|PAYMENT_SYSTEM_REPUTATION_STAKE|${PAYMENT_SYSTEM_REPUTATION_STAKE}|" \
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
									FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}/${CURRENT_DATA_FILENAME}.json"
									cp ${TEMP_CONFIG_FILENAME} ${FINAL_CONFIG_FILENAME}
									GENERATED_FILENAMES+=(${FINAL_CONFIG_FILENAME})
									COUNT=$((COUNT + 1))
								else
									if [[ ${BEHAVIOR} == "s" ]] || [[ ${BEHAVIOR} == "Ns" ]]; then
										for SCEPTICISM_THRESHOLD in ${sSCEPTICISM_THRESHOLD_LIST[*]} ; do
											CURRENT_DATA_FILENAME=$( echo ${DATA_FILENAME} | 
														sed -e "s|SCEPTICISM_THRESHOLD|${SCEPTICISM_THRESHOLD}|"  \
																	-e "s|[\.]||g")
											FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}/${CURRENT_DATA_FILENAME}.json"
											sed -e "s|SCEPTICISM_THRESHOLD|${SCEPTICISM_THRESHOLD}|" \
												${TEMP_CONFIG_FILENAME} > ${FINAL_CONFIG_FILENAME}
											GENERATED_FILENAMES+=(${FINAL_CONFIG_FILENAME})
											COUNT=$((COUNT + 1))
										done
									else
										if [[ ${BEHAVIOR} == "r" ]]; then
											for RANKING_THRESHOLD in ${rRANKING_THRESHOLD_LIST[*]} ; do
												CURRENT_DATA_FILENAME=$( echo ${DATA_FILENAME} | 
															sed -e "s|RANKING_THRESHOLD|${RANKING_THRESHOLD}|"  \
																	-e "s|[\.]||g")
												FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}/${CURRENT_DATA_FILENAME}.json"
												sed -e "s|RANKING_THRESHOLD|${RANKING_THRESHOLD}|" \
													${TEMP_CONFIG_FILENAME} > ${FINAL_CONFIG_FILENAME}
												GENERATED_FILENAMES+=(${FINAL_CONFIG_FILENAME})
												COUNT=$((COUNT + 1))
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
													FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}/${CURRENT_DATA_FILENAME}.json"
													sed -e "s|COMPARISON_METHOD|${COMPARISON_METHOD}|" \
														-e "s|SCALING|${SCALING}|" \
														-e "s|SCEPTICISM_THRESHOLD|${SCEPTICISM_THRESHOLD}|" \
														-e "s|WEIGHT_METHOD|${WEIGHT_METHOD}|" \
														${TEMP_CONFIG_FILENAME} > ${FINAL_CONFIG_FILENAME}
													GENERATED_FILENAMES+=(${FINAL_CONFIG_FILENAME})
													COUNT=$((COUNT + 1))
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
														FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}/${CURRENT_DATA_FILENAME}.json"
														sed -e "s|COMPARISON_METHOD|${COMPARISON_METHOD}|" \
															-e "s|SCALING|${SCALING}|" \
															${TEMP_CONFIG_FILENAME} > ${FINAL_CONFIG_FILENAME}
														GENERATED_FILENAMES+=(${FINAL_CONFIG_FILENAME})
														COUNT=$((COUNT + 1))
													done
													done
												else
													if [[ ${BEHAVIOR} == "h" ]]; then
														for VERIFICATION_METHOD in ${hVERIFICATION_METHOD_LIST[*]} ; do
														for THRESHOLD_METHOD in ${hTHRESHOLD_METHOD_LIST[*]} ; do
														for SCALING in ${hSCALING_LIST[*]} ; do
														for KDIFF in ${hKD_LIST[*]} ; do
															CURRENT_DATA_FILENAME=$( echo ${DATA_FILENAME} | 
																		sed -e "s|VERIFICATION_METHOD|${VERIFICATION_METHOD}|" \
																		-e "s|THRESHOLD_METHOD|${THRESHOLD_METHOD}|" \
																		-e "s|SCALING|${SCALING}|" \
																		-e "s|KDIFF|${KDIFF}|" \
																		-e "s|[\.]||g")
															FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}/${CURRENT_DATA_FILENAME}.json"
															sed -e "s|VERIFICATION_METHOD|${VERIFICATION_METHOD}|" \
																-e "s|THRESHOLD_METHOD|${THRESHOLD_METHOD}|" \
																-e "s|SCALING|${SCALING}|" \
																-e "s|KDIFF|${KDIFF}|" \
																${TEMP_CONFIG_FILENAME} > ${FINAL_CONFIG_FILENAME}
															GENERATED_FILENAMES+=(${FINAL_CONFIG_FILENAME})
															COUNT=$((COUNT + 1))
														done
														done
														done
														done
													fi
												fi
											fi
										fi
									fi
								fi
								rm ${TEMP_CONFIG_FILENAME}
							done
						done
					fi
					done
					done
				done
			done
		done
		done
		done
	else #------------------- FIXED NOISE EXPERIMENTS -------------------#
	#TODO DO NOT SIMULATE BOTH avg AND perf SABOTEURS:
	#     IF BOTH ARE IN THE LIST, SKIP perf
		AGENT_NOISE_CLASS="UniformNoise"
		AGENT_NOISE_PARAMETERS=$AGENT_UNIFORM_NOISE_PARAMETERS_TEMPLATE
		for AGENT_NOISE_MU in ${AGENT_NOISE_MU_LIST[*]} ; do
		for AGENT_NOISE_RANGE in ${AGENT_NOISE_RANGE_LIST[*]} ; do
			for BEHAVIOR in ${BEHAVIOR_LIST[*]} ; do
				for HONEST_POPULATION in ${HONEST_POPULATION_LIST[*]} ; do
					DISHONEST_POPULATION=$((NUMBER_OF_ROBOTS-HONEST_POPULATION))
					for PAYMENT_SYSTEM_CLASS in ${PAYMENT_SYSTEM_CLASS_LIST[*]} ; do
					for PAYMENT_SYSTEM_REPUTATION_STAKE in ${PAYMENT_SYSTEM_REPUTATION_STAKE_LIST[*]} ; do
					#TODO improve conditions to simulate incompatible behaviors
					if ! [[ $PAYMENT_SYSTEM_REPUTATION_STAKE == "true" ]] || ! [[ $PAYMENT_SYSTEM_CLASS == "DelayedPaymentPaymentSystem" ]]; then
					if ! [[ $PAYMENT_SYSTEM_REPUTATION_STAKE == "true" ]] || ! [[ $BEHAVIOR == "n" ]]; then
					if ! [[ $PAYMENT_SYSTEM_REPUTATION_STAKE == "true" ]] || ! [[ $BEHAVIOR == "s" ]]; then
					if ! [[ $PAYMENT_SYSTEM_REPUTATION_STAKE == "true" ]] || ! [[ $BEHAVIOR == "b" ]]; then
						for DISHONEST_LIE_ANGLE in ${DISHONEST_LIE_ANGLE_LIST[*]} ; do
						if ! [[ $DISHONEST_LIE_ANGLE == 0 ]] || ! [[ $DISHONEST_POPULATION != 0 ]]; then
						if ! [[ $DISHONEST_LIE_ANGLE != 0 ]] || ! [[ $DISHONEST_POPULATION == 0 ]]; then
							for COMBINE_STRATEGY in ${COMBINE_STRATEGY_LIST[*]} ; do
								HONEST_CLASS=${HONEST_DICTIONARY[${BEHAVIOR}]}
								DISHONEST_CLASS=${DISHONEST_DICTIONARY[${BEHAVIOR}]}
								HONEST_PARAMS=${HONEST_PARAMETERS[${BEHAVIOR}]}
								DISHONEST_PARAMS=${DISHONEST_PARAMETERS[${BEHAVIOR}]}
								COMBINE_STRATEGY_CLASS=${COMBINE_STRATEGIES[${COMBINE_STRATEGY}]}
								FILENAME_ADDITIONAL_INFO=${BEHAVIOUR_FILENAME_ADDITIONAL_INFO[${BEHAVIOR}]}
								SUB_DIR=${SUB_DIR_BEHAVIOR[${BEHAVIOR}]}
								DATA_OUTPUT_DIRECTORY="${DATA_DIR}/${SUB_DIR}"
								CONFIG_OUTPUT_DIRECTORY="${CONFIG_DIR}/${SUB_DIR}"
								FILENAME_BASE="${HONEST_POPULATION}${BEHAVIOR_INITIALS[${BEHAVIOR}]}_${COMBINE_STRATEGIES_INITIALS[${COMBINE_STRATEGY}]}CS_${PAYMENT_SYSTEM_NAME[${PAYMENT_SYSTEM_CLASS}]}_${REPUTATION_STAKING_NAME_PREFIX[${PAYMENT_SYSTEM_REPUTATION_STAKE}]}RS_${DISHONEST_LIE_ANGLE}LIA"
								FILENAME="${FILENAME_BASE}${FILENAME_ADDITIONAL_INFO}${NOISE_FILENAME_ADDITIONAL_INFO[${AGENT_NOISE_ASSIGNATION}]}"
								DATA_FILENAME="${FILENAME}"
								TEMP_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}/temp.json"

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
									-e "s|COMBINE_STRATEGY_CLASS|${COMBINE_STRATEGY_CLASS}|" \
									-e "s|PAYMENT_SYSTEM_CLASS|${PAYMENT_SYSTEM_CLASS}|" \
									-e "s|PAYMENT_SYSTEM_INITIAL_REWARD|${PAYMENT_SYSTEM_INITIAL_REWARD}|" \
									-e "s|PAYMENT_SYSTEM_INFORMATION_SHARE|${PAYMENT_SYSTEM_INFORMATION_SHARE}|" \
									-e "s|PAYMENT_SYSTEM_REPUTATION_STAKE|${PAYMENT_SYSTEM_REPUTATION_STAKE}|" \
									-e "s|MARKET_CLASS|${MARKET_CLASS}|" \
									-e "s|MARKET_REWARD|${MARKET_REWARD}|" \
									-e "s|DATA_OUTPUT_DIRECTORY|${DATA_OUTPUT_DIRECTORY}|" \
									-e "s|DATA_PRECISE_RECORDING_INTERVAL|${DATA_PRECISE_RECORDING_INTERVAL}|" \
									-e "s|DATA_TRANSACTIONS_LOG|${DATA_TRANSACTIONS_LOG}|" \
										${CONFIG_FILE_TEMPLATE} > ${TEMP_CONFIG_FILENAME}
									# -e "s|PAYMENT_SYSTEM_REPUTATION_METRIC|${PAYMENT_SYSTEM_BEHAVIOR_REPUTATION_METRIC[${BEHAVIOR}]}|" \

									DATA_FILENAME=$( echo ${DATA_FILENAME} | 
												sed -e "s|AGENT_NOISE_MU|${AGENT_NOISE_MU}|"\
												-e "s|AGENT_NOISE_RANGE|${AGENT_NOISE_RANGE}|" )
								
								# 	BEHAVIOUR PARAMS_SUBSTITUTION
								if [[ ${BEHAVIOR} == "n" ]] || [[ ${BEHAVIOR} == "Nn" ]] || [[ ${BEHAVIOR} == "w" ]]; then
									CURRENT_DATA_FILENAME=$( echo ${DATA_FILENAME} | 
												sed -e "s|[\.]||g" )
									FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}/${CURRENT_DATA_FILENAME}.json"
									# cp ${TEMP_CONFIG_FILENAME} ${FINAL_CONFIG_FILENAME}
									sed -e "s|REPUTATION_METHOD||" \
										${TEMP_CONFIG_FILENAME} > ${FINAL_CONFIG_FILENAME}
									GENERATED_FILENAMES+=(${FINAL_CONFIG_FILENAME})
									COUNT=$((COUNT + 1))
								else
									if [[ ${BEHAVIOR} == "s" ]] || [[ ${BEHAVIOR} == "Ns" ]]; then
										for SCEPTICISM_THRESHOLD in ${sSCEPTICISM_THRESHOLD_LIST[*]} ; do
											CURRENT_DATA_FILENAME=$( echo ${DATA_FILENAME} | 
														sed -e "s|SCEPTICISM_THRESHOLD|${SCEPTICISM_THRESHOLD}|"  \
																	-e "s|[\.]||g")
											FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}/${CURRENT_DATA_FILENAME}.json"
											sed -e "s|SCEPTICISM_THRESHOLD|${SCEPTICISM_THRESHOLD}|" \
												-e "s|REPUTATION_METHOD||" \
												${TEMP_CONFIG_FILENAME} > ${FINAL_CONFIG_FILENAME}
											GENERATED_FILENAMES+=(${FINAL_CONFIG_FILENAME})
											COUNT=$((COUNT + 1))
										done
									else
										if [[ ${BEHAVIOR} == "r" ]]; then
											for RANKING_THRESHOLD in ${rRANKING_THRESHOLD_LIST[*]} ; do
											for REPUTATION_METHOD in ${rREPUTATION_METHOD_LIST[*]} ; do
												CURRENT_DATA_FILENAME=$( echo ${DATA_FILENAME} | 
															sed -e "s|RANKING_THRESHOLD|${RANKING_THRESHOLD}|"  \
																-e "s|REPUTATION_METHOD|${REPUTATION_METHOD}|" \
																-e "s|[\.]||g")
												FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}/${CURRENT_DATA_FILENAME}.json"
												sed -e "s|RANKING_THRESHOLD|${RANKING_THRESHOLD}|" \
													-e "s|REPUTATION_METHOD|${REPUTATION_METHOD}|" \
													${TEMP_CONFIG_FILENAME} > ${FINAL_CONFIG_FILENAME}
												GENERATED_FILENAMES+=(${FINAL_CONFIG_FILENAME})
												COUNT=$((COUNT + 1))
											done
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
													FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}/${CURRENT_DATA_FILENAME}.json"
													sed -e "s|COMPARISON_METHOD|${COMPARISON_METHOD}|" \
														-e "s|SCALING|${SCALING}|" \
														-e "s|SCEPTICISM_THRESHOLD|${SCEPTICISM_THRESHOLD}|" \
														-e "s|WEIGHT_METHOD|${WEIGHT_METHOD}|" \
														${TEMP_CONFIG_FILENAME} > ${FINAL_CONFIG_FILENAME}
													GENERATED_FILENAMES+=(${FINAL_CONFIG_FILENAME})
													COUNT=$((COUNT + 1))
												done
												done
												done
												done
											else
												if [[ ${BEHAVIOR} == "t" ]]; then
													for COMPARISON_METHOD in ${tCOMPARISON_METHOD_LIST[*]} ; do
													for SCALING in ${tSCALING_LIST[*]} ; do
													for REPUTATION_METHOD in ${tREPUTATION_METHOD_LIST[*]} ; do
														CURRENT_DATA_FILENAME=$( echo ${DATA_FILENAME} | 
																	sed -e "s|COMPARISON_METHOD|${COMPARISON_METHOD}|" \
																	-e "s|SCALING|${SCALING}|" \
																	-e "s|REPUTATION_METHOD|${REPUTATION_METHOD}|" \
																	-e "s|[\.]||g" )
														FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}/${CURRENT_DATA_FILENAME}.json"
														sed -e "s|COMPARISON_METHOD|${COMPARISON_METHOD}|" \
															-e "s|SCALING|${SCALING}|" \
															-e "s|REPUTATION_METHOD|${REPUTATION_METHOD}|" \
															${TEMP_CONFIG_FILENAME} > ${FINAL_CONFIG_FILENAME}
														GENERATED_FILENAMES+=(${FINAL_CONFIG_FILENAME})
														COUNT=$((COUNT + 1))
													done
													done
													done
												else
													if [[ ${BEHAVIOR} == "h" ]]; then
														for VERIFICATION_METHOD in ${hVERIFICATION_METHOD_LIST[*]} ; do
														for THRESHOLD_METHOD in ${hTHRESHOLD_METHOD_LIST[*]} ; do
														for SCALING in ${hSCALING_LIST[*]} ; do
														for KDIFF in ${hKD_LIST[*]} ; do
														for REPUTATION_METHOD in ${hREPUTATION_METHOD_LIST[*]} ; do
															CURRENT_DATA_FILENAME=$( echo ${DATA_FILENAME} | 
																		sed -e "s|VERIFICATION_METHOD|${VERIFICATION_METHOD}|" \
																		-e "s|THRESHOLD_METHOD|${THRESHOLD_METHOD}|" \
																		-e "s|SCALING|${SCALING}|" \
																		-e "s|KDIFF|${KDIFF}|" \
																		-e "s|REPUTATION_METHOD|${REPUTATION_METHOD}|" \
																		-e "s|[\.]||g")
															FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}/${CURRENT_DATA_FILENAME}.json"
															sed -e "s|VERIFICATION_METHOD|${VERIFICATION_METHOD}|" \
																-e "s|THRESHOLD_METHOD|${THRESHOLD_METHOD}|" \
																-e "s|SCALING|${SCALING}|" \
																-e "s|KDIFF|${KDIFF}|" \
																-e "s|REPUTATION_METHOD|${REPUTATION_METHOD}|" \
																${TEMP_CONFIG_FILENAME} > ${FINAL_CONFIG_FILENAME}
															GENERATED_FILENAMES+=(${FINAL_CONFIG_FILENAME})
															COUNT=$((COUNT + 1))
														done
														done
														done
														done
														done
														############################
													else
														if [[ ${BEHAVIOR} == "hs" ]]; then
															for SCEPTICISM_THRESHOLD in ${hsSCEPTICISM_THRESHOLD_LIST[*]} ; do
															for VERIFICATION_METHOD in ${hVERIFICATION_METHOD_LIST[*]} ; do
															for THRESHOLD_METHOD in ${hTHRESHOLD_METHOD_LIST[*]} ; do
															for SCALING in ${hSCALING_LIST[*]} ; do
															for KDIFF in ${hKD_LIST[*]} ; do
																CURRENT_DATA_FILENAME=$( echo ${DATA_FILENAME} | 
																			sed -e "s|VERIFICATION_METHOD|${VERIFICATION_METHOD}|" \
																			-e "s|THRESHOLD_METHOD|${THRESHOLD_METHOD}|" \
																			-e "s|SCALING|${SCALING}|" \
																			-e "s|KDIFF|${KDIFF}|" \
																			-e "s|SCEPTICISM_THRESHOLD|${SCEPTICISM_THRESHOLD}|" \
																			-e "s|[\.]||g")
																FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}/${CURRENT_DATA_FILENAME}.json"
																sed -e "s|VERIFICATION_METHOD|${VERIFICATION_METHOD}|" \
																	-e "s|THRESHOLD_METHOD|${THRESHOLD_METHOD}|" \
																	-e "s|SCALING|${SCALING}|" \
																	-e "s|KDIFF|${KDIFF}|" \
																	-e "s|SCEPTICISM_THRESHOLD|${SCEPTICISM_THRESHOLD}|" \
																	${TEMP_CONFIG_FILENAME} > ${FINAL_CONFIG_FILENAME}
																GENERATED_FILENAMES+=(${FINAL_CONFIG_FILENAME})
																COUNT=$((COUNT + 1))
															done
															done
															done
															done
															done
														############################
														else
															if [[ ${BEHAVIOR} == "c" ]]; then
															for REPUTATION_METHOD in ${cREPUTATION_METHOD_LIST[*]} ; do
																	CURRENT_DATA_FILENAME=$( echo ${DATA_FILENAME} | 
																				sed -e "s|REPUTATION_METHOD|${REPUTATION_METHOD}|" \
																				-e "s|[\.]||g" )
																	FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}/${CURRENT_DATA_FILENAME}.json"
																	sed -e "s|REPUTATION_METHOD|${REPUTATION_METHOD}|" \
																		${TEMP_CONFIG_FILENAME} > ${FINAL_CONFIG_FILENAME}
																	# cp ${TEMP_CONFIG_FILENAME} ${FINAL_CONFIG_FILENAME}
																	GENERATED_FILENAMES+=(${FINAL_CONFIG_FILENAME})
																	COUNT=$((COUNT + 1))
															done
															else ##############################################
																if [[ ${BEHAVIOR} == "b" ]]; then
																for GOOD_ACCEPTANCE_RATE in ${bGOOD_ACCEPTANCE_RATE_LIST[*]} ; do
																for BAD_ACCEPTANCE_RATE in ${bBAD_ACCEPTANCE_RATE_LIST[*]} ; do
																for SABOTEUR_ACCEPTANCE_RATE in ${bSABOTEUR_ACCEPTANCE_RATE_LIST[*]} ; do
																		CURRENT_DATA_FILENAME=$( echo ${DATA_FILENAME} | 
																					sed -e "s|GOOD_ACCEPTANCE_RATE|${GOOD_ACCEPTANCE_RATE}|" \
																					-e "s|BAD_ACCEPTANCE_RATE|${BAD_ACCEPTANCE_RATE}|" \
																					-e "s|SABOTEUR_ACCEPTANCE_RATE|${SABOTEUR_ACCEPTANCE_RATE}|" \
																					-e "s|[\.]||g" )
																		FINAL_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}/${CURRENT_DATA_FILENAME}.json"
																		sed -e "s|REPUTATION_METHOD||" \
																			-e "s|GOOD_ACCEPTANCE_RATE|${GOOD_ACCEPTANCE_RATE}|" \
																			-e "s|BAD_ACCEPTANCE_RATE|${BAD_ACCEPTANCE_RATE}|" \
																			-e "s|SABOTEUR_ACCEPTANCE_RATE|${SABOTEUR_ACCEPTANCE_RATE}|" \
																			-e "s|DISHONEST_POPULATION|${DISHONEST_POPULATION}|" \
																			-e "s|HONEST_POPULATION|${HONEST_POPULATION}|" \
																			-e "s|AGENT_NOISE_ASSIGNATION|${AGENT_NOISE_ASSIGNATION}|" \
																			${TEMP_CONFIG_FILENAME} > ${FINAL_CONFIG_FILENAME}
																		# cp ${TEMP_CONFIG_FILENAME} ${FINAL_CONFIG_FILENAME}
																		GENERATED_FILENAMES+=(${FINAL_CONFIG_FILENAME})
																		COUNT=$((COUNT + 1))
																done
																done
																done
																fi
															fi
														fi
													fi
												fi
											fi
										fi
									fi
								fi
								rm ${TEMP_CONFIG_FILENAME}
							done
						fi
						fi
						done
					fi
					fi
					fi
					fi
					done
					done
				done
			done
		done
		done
	fi
done

echo "CREATED " $COUNT " CONFIGURATIONS"
