#!/bin/bash

#Directories paths
PROJECT_HOME="${HOME}/demamas/DeMaMAS"
CONF_DIR="${PROJECT_HOME}/conf_cluster"
EXEC_FILE="${PROJECT_HOME}/src/deMaMAS.py"
PLOT_DIRECTORY="${PROJECT_HOME}/analysisTool/plots/"
PYPATH="${PROJECT_HOME}/"
RESULT_FOLDER_PATH="${PROJECT_HOME}/results/"
RESULT_FOLDER_PATH_SUMMARY="${PROJECT_HOME}/results/"
CONF_FILE_SUMMARY="${RESULT_FOLDER_PATH_SUMMARY}summary.config"
SUMMARY_TEMPLATE="${PROJECT_HOME}/configuration/configuration.summary.template.config"
TEMPLATE_SETTINGS="${PROJECT_HOME}/configuration/configuration.template.config"
mkdir -p ${CONF_DIR}
mkdir -p ${RESULT_FOLDER_PATH}
mkdir -p ${RESULT_FOLDER_PATH_SUMMARY}

#USUALLY FIXED
#General parameters
TYPE="swarm"
COLORS=[gray,red,green,blue,yellow,violet,darkorange,navy,peru,turquoise,olive,cadetblue,indigo,gold,purple,pink,crimson]
COMPOSITION=1
COMP_LABELS=[CI,ZEL]
ENVIRONMENT_SIZE=1
NUM_SIMULATION=15
NUM_START_P=1
NUM_STEP=5
NUM_TOTEM=[1]
OVERLAPPING_TOTEMS="false"
QUORUM=0.75
REQUIRED_NUMBER_OF_STEP_OVER_Q=500
SEED=0
STARTING_POINT="false"
TEST_NAME=CIR
INITIAL_OPINIONS=[[0.0,0.5,0.5],[0.0,0.5,0.5]]
#COMPOSITION=[0.6,0.4]
NUM_SIMULATION_TO_REPEAT=2
#Agent and totem characteristics parameters
TOTEM_RADIUS=0
FIRST_ENTRY_ONLY_DISC="false"

#Movement parameters
MOVE_DIMENSION=0.01
STRAIGHT_LENGTH=9
STANDARD_DEVIATION_VALUE=1

#Behaviour parameters
DISCOVERY_METHOD=[probabilistic,probabilistic]
PROBABILISTIC_DISCOVERY_PROPORTION=[difference,difference]
K_UNANIMITY_PARAMETER=2
MAX_QUALITY=1
ZEALOT_QUALITY=[1,1]

#Message parameters
MSG_TYPE=simple
SEND_METHOD=[wv,wv]
SEND_CONSTANT_INTERVAL=1
FILTER_MSG_PARAM=[0,0]

#Decay parameters
DECAY_METHOD=[constant,constant]
DECAY_STRENGTH=[0,0]

#Interaction function parameters
PRE_STEP_SOCIAL_STRENGTH=[1,1]
POST_STEP_SOCIAL_STRENGTH=[1,1]
PRE_STEP_SELF_STRENGTH=[0.0,0.0]
POST_STEP_SELF_STRENGTH=[0.0,0.0]
INTERACTIVE_PROBABILITY=0.05
INTERACTION_FUNCTION=[constant,constant]
INITIAL_TIME_VALUE=400
#Files parameters
COLOURS_FILE=[0,R,B,G,Y,V,D,N,P,T,O,C,I,Go,Pu,Pi,Cr]
STATISTICS_FILENAME=statistic_
FINAL_RESULT_FILENAME=Result.txt

#Graphic and plot parameters
ANIMATION_INTERVAL=50
GRAPH_SIMULATION="false"
PLOT="false"


#USUALLY CHANGE

#Values that iterate for different configuration files
QUALITY_VALUES_LIST=([1,1])
NUMBER_OF_OPINIONS_LIST=(2)
DEVIATION_VALUE_LIST=(1)
COMPOSITION_LIST=([0.88,0.12])
#COMPOSITION_LIST=([1,0] [0.99,0.01] [0.98,0.02] [0.97,0.03] [0.96,0.04] [0.95,0.05] [0.94,0.06] [0.93,0.07] [0.92,0.08] [0.91,0.09] [0.9,0.1] [0.89,0.11] [0.88,0.12] [0.87,0.13] [0.86,0.14] [0.85,0.15] [0.84,0.16] [0.83,0.17] [0.82,0.18] [0.81,0.19] [0.8,0.2] [0.79,0.21] [0.78,0.22] [0.77,0.23] [0.76,0.24] [0.75,0.25] [0.74,0.26] [0.73,0.27] [0.72,0.28] [0.71,0.29] [0.7,0.3] [0.69,0.31] [0.68,0.32] [0.67,0.33] [0.66,0.34] [0.65,0.35] [0.64,0.36] [0.63,0.37] [0.62,0.38] [0.61,0.39] [0.6,0.4] [0.59,0.41] [0.58,0.42] [0.57,0.43] [0.56,0.44] [0.55,0.45] [0.54,0.46] [0.53,0.47] [0.52,0.48] [0.51,0.49] [0.5,0.5] [0.49,0.51] [0.48,0.52] [0.47,0.53] [0.46,0.54] [0.45,0.55] [0.44,0.56] [0.43,0.57] [0.42,0.58] [0.41,0.59] [0.4,0.60] [0.39,0.61] [0.38,0.62] [0.37,0.63] [0.36,0.64] [0.35,0.65] [0.34,0.66] [0.33,0.67] [0.32,0.68] [0.31,0.69] [0.3,0.70] [0.29,0.71] [0.28,0.72] [0.27,0.73] [0.26,0.74] [0.25,0.75] [0.24,0.76] [0.23,0.77] [0.22,0.78] [0.21,0.79] [0.2,0.8] [0.19,0.81] [0.18,0.82] [0.17,0.83] [0.16,0.84] [0.15,0.85] [0.14,0.86] [0.13,0.87] [0.12,0.88] [0.11,0.89] [0.1,0.9] [0.09,0.91] [0.08,0.92] [0.07,0.93] [0.06,0.94] [0.05,0.95] [0.04,0.96] [0.03,0.97] [0.02,0.98] [0.01,0.99] [0,1])
#COMPOSITION_LIST=([1,0] [0.99,0.01] [0.98,0.02] [0.97,0.03] [0.96,0.04] [0.95,0.05] [0.94,0.06] [0.93,0.07] [0.92,0.08] [0.91,0.09] [0.9,0.1] [0.89,0.11] [0.88,0.12] [0.87,0.13] [0.86,0.14] [0.85,0.15] [0.84,0.16] [0.83,0.17] [0.82,0.18] [0.81,0.19] [0.8,0.2] [0.79,0.21] [0.78,0.22] [0.77,0.23] [0.76,0.24] [0.75,0.25] [0.74,0.26] [0.73,0.27] [0.72,0.28] [0.71,0.29] [0.7,0.3])
NUMBER_OF_AGENTS=(200)
#INTERACTION_FUNCTION_LIST=([constant])
INITIAL_TIME_VALUE_LIST=(400)
UPDATE_MODEL_LIST=([direct,direct] [crossInhibition,crossInhibition])
UPDATE_RULE_LIST=([random,mad] [majority,mad])
#Values for summary.config
DEVIATION_VALUES_SUMMARY=([1])
#DIFFICULTY_VALUES_SUMMARY=([0.4,0.8])
NUMBER_OF_AGENTS_SUMMARY=([200])
AGENT_RADIUS_LIST=(0.03 0.05 0.07 0.09 0.11 0.13 0.15 0.17 0.2)
NUMBER_OF_ROWS=2
NUMBER_OF_COLUMNS=3
PLOT_SINGLE_RESULTS="true"
TEST_NAME_LIST=([CI])
#AGENT_RADIUS=0.05

#SUMMARY
#Create the summary that will be used for plotting
sed -e "s|STANDARD_DEVIATION_VALUES|${DEVIATION_VALUES_SUMMARY}|" \
	-e "s|DIFFICULTY_VALUES|${DIFFICULTY_VALUES_SUMMARY}|" \
	-e "s|NUMBER_OF_OPINIONS|${NUMBER_OF_OPINIONS_LIST}|" \
	-e "s|NUMBER_OF_AGENTS|${NUMBER_OF_AGENTS_SUMMARY}|" \
	-e "s|NUMBER_OF_STEPS|${NUM_STEP}|" \
	-e "s|NUMBER_OF_SIMULATIONS|${NUM_SIMULATION}|" \
	-e "s|COLORS|${COLORS}|" \
	-e "s|COMPOSITION_LIST|${COMPOSITION_LIST}|" \
	-e "s|NUMBER_OF_COLUMNS|${NUMBER_OF_COLUMNS}|" \
	-e "s|NUMBER_OF_ROWS|${NUMBER_OF_ROWS}|" \
	-e "s|PLOT_DIRECTORY|${PLOT_DIRECTORY}|" \
	-e "s|PLOT_SINGLE_RESULTS|${PLOT_SINGLE_RESULTS}|" \
	-e "s|TEST_NAME_LIST|${TEST_NAME_LIST}|" \
		${SUMMARY_TEMPLATE} > ${CONF_FILE_SUMMARY}

COUNT=0
#CONFIGURATIONS FILES CREATION
#Create all the configuration files
for QUALITY_VALUES in ${QUALITY_VALUES_LIST[*]}
do
	for NUM_OP in ${NUMBER_OF_OPINIONS_LIST[*]}
	do
			for NUM_AGENT in ${NUMBER_OF_AGENTS[*]}
			do
					for INITIAL_TIME_VALUE in ${INITIAL_TIME_VALUE_LIST[*]}
					do
					     for AGENT_RADIUS in ${AGENT_RADIUS_LIST[*]}
					     do
						for COMPOSITION in ${COMPOSITION_LIST[*]}
						do
							for UPDATE_MODEL in ${UPDATE_MODEL_LIST[*]}
							do
								for UPDATE_RULE in ${UPDATE_RULE_LIST[*]}
								do
								for ((i=1;i<=${NUM_SIMULATION_TO_REPEAT};i++)); 
								do

									JOB_PARAM="t-${NUM_TOTEM}_agt-${NUM_AGENT}_stp-${NUM_STEP}_op-${NUM_OP}_maxQ-${MAX_QUALITY}_qVl-${QUALITY_VALUES}_mdl-${UPDATE_MODEL}_rle-${UPDATE_RULE}_dscv-${DISCOVERY_METHOD}_qrm-${QUORUM}_stdDv-${STANDARD_DEVIATION_VALUE}_intrct-${INTERACTION_FUNCTION}_iniT-${INITIAL_TIME_VALUE}_cmps-${COMPOSITION}_tstN-${TEST_NAME}_agtRadius-${AGENT_RADIUS}"
									JOB_CHANGING_PARAM="rle-${UPDATE_RULE}_${UPDATE_MODEL}_qvl-${QUALITY_VALUES}_op-${NUM_OP}_stdDv-${STANDARD_DEVIATION_VALUE}_agt-${NUM_AGENT}_intrct-${INTERACTION_FUNCTION}_iniT-${INITIAL_TIME_VALUE}_cmps-${COMPOSITION}_agtR-${AGENT_RADIUS}"
								        EXP_RESULT_FOLDER_PATH="${RESULT_FOLDER_PATH}/${JOB_CHANGING_PARAM}/"
									CONF_FILE="${CONF_DIR}/demamas_${JOB_PARAM}.config"
									sed -e "s|SEED|${SEED}|" \
										-e "s|ENVIRONMENT_SIZE|${ENVIRONMENT_SIZE}|" \
										-e "s|MOVE_DIMENSION|${MOVE_DIMENSION}|" \
										-e "s|NUM_AGENT|${NUM_AGENT}|" \
										-e "s|AGENT_RADIUS|${AGENT_RADIUS}|" \
										-e "s|TOTEM_RADIUS|${TOTEM_RADIUS}|" \
										-e "s|FIRST_ENTRY_ONLY_DISC|${FIRST_ENTRY_ONLY_DISC}|" \
										-e "s|NUM_STEP|${NUM_STEP}|" \
										-e "s|STRAIGHT_LENGTH|${STRAIGHT_LENGTH}|" \
										-e "s|MAX_QUALITY|${MAX_QUALITY}|" \
										-e "s|COLORS|${COLORS}|" \
										-e "s|COMPOSITION|${COMPOSITION}|" \
										-e "s|COMP_LABELS|${COMP_LABELS}|" \
										-e "s|COLOURS_FILE|${COLOURS_FILE}|" \
										-e "s|QUALITY_VALUES|${QUALITY_VALUES}|" \
										-e "s|NUM_OP|${NUM_OP}|" \
										-e "s|NUM_TOTEM|${NUM_TOTEM}|" \
										-e "s|OVERLAPPING_TOTEMS|${OVERLAPPING_TOTEMS}|" \
										-e "s|STARTING_POINT|${STARTING_POINT}|" \
										-e "s|NUM_START_P|${NUM_START_P}|" \
										-e "s|UPDATE_MODEL|${UPDATE_MODEL}|" \
										-e "s|SEND_METHOD|${SEND_METHOD}|" \
										-e "s|SEND_CONSTANT_INTERVAL|${SEND_CONSTANT_INTERVAL}|" \
										-e "s|FILTER_MSG_PARAM|${FILTER_MSG_PARAM}|" \
										-e "s|MSG_TYPE|${MSG_TYPE}|" \
										-e "s|UPDATE_RULE|${UPDATE_RULE}|" \
										-e "s|INITIAL_OPINIONS|${INITIAL_OPINIONS}|" \
										-e "s|ZEALOT_QUALITY|${ZEALOT_QUALITY}|" \
										-e "s|K_UNANIMITY_PARAMETER|${K_UNANIMITY_PARAMETER}|" \
										-e "s|DISCOVERY_METHOD|${DISCOVERY_METHOD}|" \
										-e "s|PROBABILISTIC_DISCOVERY_PROPORTION|${PROBABILISTIC_DISCOVERY_PROPORTION}|" \
										-e "s|ANIMATION_INTERVAL|${ANIMATION_INTERVAL}|" \
										-e "s|QUORUM|${QUORUM}|" \
										-e "s|REQUIRED_NUMBER_OF_STEP_OVER_Q|${REQUIRED_NUMBER_OF_STEP_OVER_Q}|" \
										-e "s|RESULT_FOLDER_PATH|${EXP_RESULT_FOLDER_PATH}|" \
										-e "s|STATISTICS_FILENAME|${STATISTICS_FILENAME}|" \
										-e "s|FINAL_RESULT_FILENAME|${FINAL_RESULT_FILENAME}|" \
										-e "s|NUM_SIMULATION|${NUM_SIMULATION}|" \
										-e "s|GRAPH_SIMULATION|${GRAPH_SIMULATION}|" \
										-e "s|PLOT|${PLOT}|" \
										-e "s|DECAY_METHOD|${DECAY_METHOD}|" \
										-e "s|DECAY_STRENGTH|${DECAY_STRENGTH}|" \
										-e "s|STANDARD_DEVIATION_VALUE|${STANDARD_DEVIATION_VALUE}|" \
										-e "s|PRE_STEP_SOCIAL_STRENGTH|${PRE_STEP_SOCIAL_STRENGTH}|" \
										-e "s|POST_STEP_SOCIAL_STRENGTH|${POST_STEP_SOCIAL_STRENGTH}|" \
										-e "s|PRE_STEP_SELF_STRENGTH|${PRE_STEP_SELF_STRENGTH}|" \
										-e "s|POST_STEP_SELF_STRENGTH|${POST_STEP_SELF_STRENGTH}|" \
										-e "s|INTERACTION_FUNCTION|${INTERACTION_FUNCTION}|" \
										-e "s|INITIAL_TIME_VALUE|${INITIAL_TIME_VALUE}|" \
										-e "s|INTERACTIVE_PROBABILITY|${INTERACTIVE_PROBABILITY}|" \
										-e "s|TEST_NAME|${TEST_NAME}|" \
										-e "s|TYPE|${TYPE}|" \
											${TEMPLATE_SETTINGS} > ${CONF_FILE}

									export PYTHONPATH=${PYPATH}
									COMMAND="python ${EXEC_FILE} ${CONF_FILE}"
									#COMMAND="./run_job.sh ${EXEC_FILE} ${CONF_FILE}"
									#COMMAND="sbatch run_job.sh ${EXEC_FILE} ${CONF_FILE}"
									echo "${COMMAND}"
									while ! ${COMMAND}
									do
										sleep 2
									done
									COUNT=$((COUNT + 1))
								done
								done
							done 
							done
						done
					done
			done
	done
done

echo "Submitted " $COUNT " jobs"
