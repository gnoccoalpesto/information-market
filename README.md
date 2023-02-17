# Master's Thesis: An Information Market for Social Navigation in Robots
## Requirements
To be able to run information-market, you must have:
- A recent version of Linux, MacOSX or Windows
- **Python** 3.10 or newer
## Installation
First clone the git repository into a given folder on your computer:
```bash
git clone https://github.com/ludericv/information-market.git
```
Then, navigate into the newly created folder, create a new python virtual environment and install the required python packages:
```bash
cd information-market
python -m venv infomarket-env
source infomarket-env/bin/activate
pip install -r requirements.txt
```
## Run
First, edit the `config.json` file inside the config folder with the parameters you want to use. Then, to run information-market, simply open a terminal, cd to the src folder and run the program.
```bash
cd path/to/src
python info_market.py ../config/config.json
```

## Running Multiple Experiments
To conduct multiple experiments with different configurations, one can specify multiple configuration file paths as arguments when running the `info_market.py` script, interposing a space between the selected files. Example:
```bash
cd path/to/src
python info_market.py path/to/config1.json path/to/config2.json path/to/config99.json
```
This is mostly useful to run simulations without the GUI (set `activate` to false in the visualization parameters in the config files, as well as the `number_runs` parameter for the number of simulations you wish to perform with this configuration)

## Configuration

A simulation's parameters are defined in a json configuration file (such as `config/config.json`). The parameters are the following:

- width: simulation environment's width
- height: simulation environment's height
- food: food area's position and radius
- nest: nest area's position and radius
- simulation_steps: simulation duration (number or time steps)
- number_runs: number of parallel simulation runs (only applicable when visualization is turned off)
- simulation_seed: the base seed for the simulation. Accepted values are:
  - an integer, or a string (seeder activated)
  - empty string ("") or keyword "random" (seeder deactivated)<br />
For more informations, refer to the [Randomization](#randomization) section.
- visualization: parameters related to the visualization
  - activate: whether to activate the simulation GUI
  - fps: maximum framerate of the simulation
- random_walk: random walk parameters
  - random_walk_factor: controls how much successive random walk turns are correlated
  - levi_factor: controls the duration before successive random walk turns
- agent: robot parameters (common to all robots regardless of behavior)
  - radius: robot radius
  - speed: robot speed
  - communication_radius: communication range
  - communication_stop_time: duration a robot must stop moving when communicating
  - communication_cooldown: how long a robot must wait between communications
  - noise_sampling_mu: odometric noise sampling distribution mu
  - noise_sampling_sigma: odometric noise sampling distribution sigma
  - noise_sd: odometric noise standard deviation (in degrees), i.e. how different the odometric noise at different time steps
  - fuel_cost: cost of moving at each time step (deducted from robot's monetary balance)
- behaviors: list of behaviors used in the simulation
  - class: name of the behavior class (from the code, see [Behaviors](#behaviors) section)
  - population_size: number of robots with the behavior
  - parameters: behavior-specific keyword arguments
- payment_system: payment system parameters
  - class: name of the payment system class (from the code, see [Payment Systems](#payment-systems) section)
  - initial_reward: amount of money robots start the simulation with
  - parameters: payment-system-specific keyword arguments
- market: reward mechanism parameters
  - class: name of the market class (from the code, use "FixedPriceMarket", others are deprecated)
  - parameters: market-specific parameters
    - reward: reward for selling a strawberry at the nest
- data_collection: parameters for data collection
  - output_directory: output directory path.
  - filename: output data filename. File will be saved to <output_directory>/<metric>/<filename> for all metrics in metrics parameter. If empty, an automatic title will be generated in this way:<br />
   "{N_naives+N_scepticals}scepticals_{3000 if N_naive>0 and N_scepticals==0 else Thresh_scepticals}th_{N_saboteurs+N_scaboteurs}scaboteurs_{lie_angle}rotation_<br />{'no' if no_penalisation else ''}penalisation_{SEED if SEED!="" or "random" else "random"}Seed.csv".
  - metrics: list of metrics to record.<br />
  Accepted metrics: "rewards", "items_collected", "drifts" "items_evolution" or "rewards_evolution").<br />When "rewards_evolution" or "items_evolutions" are included in the metrics, `Precise recording` mode is activated and the specified data will be saved at multiple time steps during the simulation.
  - precise_recording_interval: resolution (in number of time steps) for the `Precise recording`.

## Behaviors

Robots can exhibit multiple behaviors. This sections briefly lists these behaviors and their parameters.

- `NaiveBehavior`: Most basic robot behavior. Simply exchanges information with everyone and uses the most recent information available.
- `SaboteurBehavior`: Basic dishonest robot behavior. Rotates information vectors sold to other robots by a given angle.
  - parameters: 
    - `rotation_angle`: angle (in degrees) with which information vectors are rotated when sold.
- `ScepticalBehavior`: Honest robot behavior implementing basic outlier detection. If information is too different from previous belief is bought, the robot will wait until receiving information confirming the new statement or the old belief before accepting or rejecting the new information.
  - parameters:
    - `threshold`: controls how much new information can be different from previous belief before being considered suspicious and needing confirmation.
- `ScaboteurBehavior`: Saboteur behavior implementing the outlier detection from the ScepticalBehavior
  - parameters:
    - `threshold`: see ScepticalBehavior
    - `rotation_angle`: see SaboteurBehavior

## Payment Systems

Payment systems implement the logic responsible for controlling the price of information.

- `DelayedPaymentPaymentSystem`: information is exchanged for a token that is redeemed for a fixed share of the reward the buying robot receives when it completes a round trip.
- `OutlierPenalisationPaymentSystem`: similar to the DelayedPaymentPayment system, but the share of the reward is proportional to how similar the information sold is to other information that was sold to the buying robot.

## Randomization

Seeding the random number generator is useful when repeating experiments is needed.<br />
If empty string ("") or "random" is passed in the configuration, the simulation utilizes a different seed for each time a random function is called.<br /> Otherwise, the passed seed is used as base, increased by the number of the run.

## Visual Simulation and Hotkeys

During a simulation with GUI (`activate` : true in the configuration file), you can select a robot (left click on its image) and observe useful datas about it.

You can also use your keyboard to control the course of the simulation:
- `SPACE`: pause/resume simulation;
- `N`: perform one step of the simulation (useful when paused);
- `0`: cycles selection between robots with id in the range 0-9;
- `1`: cycles selection between robots with id in the range 10-19;
- `2`: cycles selection between robots with id in the range 20-MAX_ID_ROBOT;
- `+`: selects the robot with +1 id with respect to the current selection;
- `-`: selects the robot with -1 id with respect to the current selection;
- `c`: selects back the robot in the +/- keys counter;
