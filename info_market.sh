#!/bin/bash

PROJECT_HOME="${HOME}/ing/tesi/information-market/"
CONFIG_DIR="${PROJECT_HOME}config/"
EXEC_FILE="${PROJECT_HOME}src/info_market.py"
# PLOT_DIRECTORY="${PROJECT_HOME}/plots/"
# PYPATH="${PROJECT_HOME}/"
DATA_DIR="${PROJECT_HOME}data/"
# CONFIG_FILE_TEMPLATE="${CONFIG_DIR}config_template"
CONFIG_FILE_TEMPLATE="${CONFIG_DIR}config_template"
# CONF_FILE_SUMMARY="${DATA_DIR_SUMMARY}summary.config"
# SUMMARY_TEMPLATE="${PROJECT_HOME}/configuration/configuration.summary.template.config"
# TEMPLATE_SETTINGS="${PROJECT_HOME}/configuration/configuration.template.config"


#GENERAL PARAMETERS ####################################################

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

#simulation
SIMULATION_STEPS=15000
SIMULATION_SEED=5684436

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

#data collection
DATA_PRECISE_RECORDING_INTERVAL=100


#EXPERIMENT PARAMS #########################################################################

#simulation
NUMBER_RUNS=32

#visualisation
VISUALISATION_ACTIVATE=false

#agent
AGENT_NOISE_ASSIGNATION_LIST=("bimodal")
# "bimodal"=="random", fixed, saboteurs: "average" "perfect"
AGENT_NOISE_SAMPLING_MU_LIST=(0.05)
AGENT_NOISE_SAMPLING_SIGMA_LIST=(0.05)
AGENT_NOISE_SD_LIST=(0.05)

#behaviours
BEHAVIOR_LIST=("n" "Nn" "s" "Ns" "r" "v" "Nv" "t" "w")
# BEHAVIOR_LIST=("v")
NUMBER_OF_ROBOTS=25
HONEST_POPULATION_LIST=(25 22)
DISHONEST_LIE_ANGLES=(90)

# BEHAVIOURS
# naive: n
# -params:{}
# -new naive: Nn
# -params:{}
# sceptical: s
# -params:{threshold}
# new sceptical: Ns
# -params:{scepticism_threshold}
# ranking: r
# -params:{ranking_threshold}
# variable scepticism: v
# -params:{comparison_method,scaling,scepticism_threshold,weight_method}
# new variable scepticism: Nv
# -params:{comparison_method,scaling,scepticism_threshold,weight_method}
# wealth weighted: w
# -params:{}
# wealth threshold: t
# -params:{comparison_method,scaling}
SCEPTICISM_THRESHOLD_LIST=(0.25)
RANKING_THRESHOLD_LIST=(0.3 0.5 0.7)
COMPARISON_METHOD_LIST=()
SCALING_LIST=()
WEIGHT_METHOD_LIST=()

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
DISHONEST_TEMPLATE='{\n\t\t"class": "DISHONEST_CLASS",\n\t\t"population_size": DISHONEST_POPULATION,\n\t\t"parameters": {\n\t\t\t"lie_angle": DISHONEST_LIE_ANGLE,\n\t\t\tHONEST_PARAMS\n\t\t\t}\n\t\t}'
BEHAVIOUR_TEMPLATE="${HONEST_TEMPLATE},\n\t\t${DISHONEST_TEMPLATE}"

declare -A BEHAVIOR_PARAMETERS
	BEHAVIOR_PARAMETERS[n]=""
	BEHAVIOR_PARAMETERS[Nn]=""
	BEHAVIOR_PARAMETERS[s]="\"threshold\": SCEPTICISM_THRESHOLD"
	BEHAVIOR_PARAMETERS[Ns]="\"scepticism_threshold\": SCEPTICISM_THRESHOLD"
	BEHAVIOR_PARAMETERS[r]="\"ranking_threshold\": RANKING_THRESHOLD"
	BEHAVIOR_PARAMETERS[v]="\"comparison_method\": \"COMPARISON_METHOD\",\n\t\t\t\"scaling\": SCALING,\n\t\t\t\"scepticism_threshold\": SCEPTICISM_THRESHOLD,\n\t\t\t\"weight_method\": \"WEIGHT_METHOD\""
	BEHAVIOR_PARAMETERS[Nv]="\"comparison_method\": \"COMPARISON_METHOD\",\n\t\t\t\"scaling\": SCALING,\n\t\t\t\"scepticism_threshold\": SCEPTICISM_THRESHOLD,\n\t\t\t\"weight_method\": \"WEIGHT_METHOD\""
	BEHAVIOR_PARAMETERS[w]=""
	BEHAVIOR_PARAMETERS[t]="\"comparison_method\": \"COMPARISON_METHOD\",\n\"scaling\": SCALING"

declare -A BEHAVIOR_NAME
	BEHAVIOR_NAME[n]="n"
	BEHAVIOR_NAME[Nn]="Nn"
	BEHAVIOR_NAME[s]="s"
	BEHAVIOR_NAME[Ns]="Ns"
	BEHAVIOR_NAME[r]="r"
	BEHAVIOR_NAME[v]="v"
	BEHAVIOR_NAME[Nv]="Nv"
	BEHAVIOR_NAME[t]="t"
	BEHAVIOR_NAME[w]="w"

declare -A SUB_DIR_BEHAVIOR
	SUB_DIR_BEHAVIOR[n]="naive/"
	SUB_DIR_BEHAVIOR[Nn]="new_naive/"
	SUB_DIR_BEHAVIOR[s]="sceptical/"
	SUB_DIR_BEHAVIOR[Ns]="new_sceptical/"
	SUB_DIR_BEHAVIOR[r]="ranking/"
	SUB_DIR_BEHAVIOR[v]="variable_scepticism/"
	SUB_DIR_BEHAVIOR[Nv]="new_variable_scepticism/"
	SUB_DIR_BEHAVIOR[t]="wealth_threshold/"
	SUB_DIR_BEHAVIOR[w]="wealth_weighted/"
	
declare -A DATA_FILENAME_ADDITIONAL_INFO
	DATA_FILENAME_ADDITIONAL_INFO[n]=""
	DATA_FILENAME_ADDITIONAL_INFO[Nn]=""
	DATA_FILENAME_ADDITIONAL_INFO[s]="_SCEPTICISM_THRESHOLDst"
	DATA_FILENAME_ADDITIONAL_INFO[Ns]="_SCEPTICISM_THRESHOLDst"
	DATA_FILENAME_ADDITIONAL_INFO[r]="_RANKING_THRESHOLDrt"
	DATA_FILENAME_ADDITIONAL_INFO[v]="_COMPARISON_METHODCm_SCALINGsc_SCEPTICISM_THRESHOLDst_WEIGHT_METHODWm"
	DATA_FILENAME_ADDITIONAL_INFO[Nv]="_COMPARISON_METHODCm_SCALINGsc_SCEPTICISM_THRESHOLDst_WEIGHT_METHODWm"
	DATA_FILENAME_ADDITIONAL_INFO[t]="_COMPARISON_METHODCm_SCALINGsc"
	DATA_FILENAME_ADDITIONAL_INFO[w]=""

declare -A PAYMENT_SYSTEM_NAME
	PAYMENT_SYSTEM_NAME[OutlierPenalisationPaymentSystem]="p"
	PAYMENT_SYSTEM_NAME[DelayedPaymentPaymentSystem]="np"

declare -A NOISE_TYPE_NAME
	NOISE_TYPE_NAME["bimodal"]=""
	NOISE_TYPE_NAME["average"]="_avg"
	NOISE_TYPE_NAME["perfect"]="_perf"

#payment system
# PAYMENT_SYSTEM_CLASS=("OutlierPenalisationPaymentSystem")
# PAYMENT_SYSTEM_CLASS=("DelayedPaymentPaymentSystem")
PAYMENT_SYSTEM_CLASS_LIST=("OutlierPenalisationPaymentSystem" "DelayedPaymentPaymentSystem")

#data collection
DATA_TRANSACTIONS_LOG=false


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

for AGENT_NOISE_ASSIGNATION in ${AGENT_NOISE_ASSIGNATION_LIST[*]} ; do
	for AGENT_NOISE_SAMPLING_MU in ${AGENT_NOISE_SAMPLING_MU_LIST[*]} ; do
		for AGENT_NOISE_SAMPLING_SIGMA in ${AGENT_NOISE_SAMPLING_SIGMA_LIST[*]} ; do
			for AGENT_NOISE_SD in ${AGENT_NOISE_SD_LIST[*]} ; do
				for BEHAVIOR in ${BEHAVIOR_LIST[*]} ; do
				# for BEHAVIORS in ${!BEHAVIOR_PARAMETERS[@]}; do #retrieved as dict keys
					for HONEST_POPULATION in ${HONEST_POPULATION_LIST[*]} ; do
						DISHONEST_POPULATION=$((NUMBER_OF_ROBOTS-HONEST_POPULATION))
						for PAYMENT_SYSTEM_CLASS in ${PAYMENT_SYSTEM_CLASS_LIST[*]} ; do
							for DISHONEST_LIE_ANGLE in ${DISHONEST_LIE_ANGLES[*]} ; do
								HONEST_CLASS=${HONEST_DICTIONARY[${BEHAVIOR}]}
								DISHONEST_CLASS=${DISHONEST_DICTIONARY[${BEHAVIOR}]}
								BEHAVIOR_PARAMS=${BEHAVIOR_PARAMETERS[${BEHAVIOR}]}
								FILENAME_ADDITIONAL_INFO=${DATA_FILENAME_ADDITIONAL_INFO[${BEHAVIOR}]}
								SUB_DIR=${SUB_DIR_BEHAVIOR[${BEHAVIOR}]}

								#TODO append noise type and statistical significant data
								DATA_OUTPUT_DIRECTORY="${DATA_DIR}${SUB_DIR}"
								CONFIG_OUTPUT_DIRECTORY="${CONFIG_DIR}${SUB_DIR}"
								FILENAME_BASE="${HONEST_POPULATION}${BEHAVIOR_NAME[${BEHAVIOR}]}_${PAYMENT_SYSTEM_NAME[${PAYMENT_SYSTEM_CLASS}]}_${DISHONEST_LIE_ANGLE}r"
								FILENAME="${FILENAME_BASE}${FILENAME_ADDITIONAL_INFO}${NOISE_TYPE_NAME[${AGENT_NOISE_ASSIGNATION}]}"
								if [[ "${AGENT_NOISE_ASSIGNATION}" != "bimodal" ]]; then
									FILENAME="${FILENAME}_${AGENT_NOISE_SAMPLING_MU}mu_${AGENT_NOISE_SAMPLING_SIGMA}sd"
								fi
								DATA_FILENAME="${FILENAME}.csv"
								# CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}${FILENAME}.json"
								TEMP_CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}temp.json"

								mkdir -p ${CONFIG_OUTPUT_DIRECTORY}

								sed -e "s|WIDTH|${WIDTH}|" \
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
									-e "s|AGENT_NOISE_ASSIGNATION|${AGENT_NOISE_ASSIGNATION}|" \
									-e "s|AGENT_NOISE_SAMPLING_MU|${AGENT_NOISE_SAMPLING_MU}|" \
									-e "s|AGENT_NOISE_SAMPLING_SIGMA|${AGENT_NOISE_SAMPLING_SIGMA}|" \
									-e "s|AGENT_NOISE_SD|${AGENT_NOISE_SD}|" \
									-e "s|AGENT_FUEL_COST|${AGENT_FUEL_COST}|" \
									-e "s|BEHAVIOURS|${BEHAVIOUR_TEMPLATE}|" \
									-e "s|PAYMENT_SYSTEM_CLASS|${PAYMENT_SYSTEM_CLASS}|" \
									-e "s|PAYMENT_SYSTEM_INITIAL_REWARD|${PAYMENT_SYSTEM_INITIAL_REWARD}|" \
									-e "s|PAYMENT_SYSTEM_INFORAMTION_SHARE|${PAYMENT_SYSTEM_INFORAMTION_SHARE}|" \
									-e "s|MARKET_CLASS|${MARKET_CLASS}|" \
									-e "s|MARKET_REWARD|${MARKET_REWARD}|" \
									-e "s|DATA_OUTPUT_DIRECTORY|${DATA_OUTPUT_DIRECTORY}|" \
									-e "s|DATA_FILENAME|${DATA_FILENAME}|" \
									-e "s|DATA_PRECISE_RECORDING_INTERVAL|${DATA_PRECISE_RECORDING_INTERVAL}|" \
									-e "s|DATA_TRANSACTIONS_LOG|${DATA_TRANSACTIONS_LOG}|" \
										${CONFIG_FILE_TEMPLATE} > ${TEMP_CONFIG_FILENAME}


								sed -i 	s/"DISHONEST_CLASS"/"${DISHONEST_CLASS}"/g ${TEMP_CONFIG_FILENAME}
								sed -i 	s/"HONEST_CLASS"/"${HONEST_CLASS}"/g ${TEMP_CONFIG_FILENAME}
								sed -i 	s/"DISHONEST_POPULATION"/"${DISHONEST_POPULATION}"/g ${TEMP_CONFIG_FILENAME}
								sed -i 	s/"HONEST_POPULATION"/"${HONEST_POPULATION}"/g ${TEMP_CONFIG_FILENAME}
								sed -i 	s/"DISHONEST_LIE_ANGLE"/"${DISHONEST_LIE_ANGLE}"/g ${TEMP_CONFIG_FILENAME}
								sed -i 	s/"HONEST_PARAMS"/"${BEHAVIOR_PARAMS}"/g ${TEMP_CONFIG_FILENAME}		

								#PARAMS_SUBSTITUTION
								if [[ ${BEHAVIOR} == "n" ]] || [[ ${BEHAVIOR} == "Nn" ]] || [[ ${BEHAVIOR} == "w" ]]; then
								
								else
								if [[ ${BEHAVIOR} == "s" ]] || [[ ${BEHAVIOR} == "Ns" ]]; then
								
								else
								if [[ ${BEHAVIOR} == "r" ]]; then
								
								else
								if [[ ${BEHAVIOR} == "v"]] || [[ ${BEHAVIOR} == "v"]]; then
								
								else
								if [[ ${BEHAVIOR} == "t"]]; then
								
								else #if [[ ${BEHAVIOR} == "w"]]; then

								fi
								fi
								fi
								fi
								fi

								#FILENAMES SUBSTITUTION
								DATA_FILENAME="${FILENAME}.csv"
								CONFIG_FILENAME="${CONFIG_OUTPUT_DIRECTORY}${FILENAME}.json"

								# export PYTHONPATH=${PYPATH}
								# COMMAND="python ${EXEC_FILE} ${CONF_FILE}"
								# #COMMAND="./run_job.sh ${EXEC_FILE} ${CONF_FILE}"
								# #COMMAND="sbatch run_job.sh ${EXEC_FILE} ${CONF_FILE}"
								# echo "${COMMAND}"
								# while ! ${COMMAND}
								# do
								# 	sleep 2
								# done
							done
						done
					done
				done
			done
		done
	done
done
