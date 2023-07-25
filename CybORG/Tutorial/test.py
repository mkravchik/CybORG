import random
import inspect
from os.path import dirname
from pprint import pprint
import argparse
import sys
from CybORG import CybORG
from CybORG.Simulator.Scenarios import FileReaderScenarioGenerator
from CybORG.Agents import B_lineAgent, KillchainAgent, RedMeanderAgent, BlueReactRemoveAgent, BlueReactRestoreAgent, HeuristicRed
from CybORG.Agents.Wrappers import RedTableWrapper, BlueTableWrapper, TrueTableWrapper
from CybORG.Agents.Wrappers.TrueTableWrapper import true_obs_to_table

# def step_red(obs, verbose=True):
#     action = agent.get_action(obs,action_space)
#     results = env.step(action=action,agent='Red')
#     obs = results.observation
    
#     if verbose:
#         print('Red Action:',action)
#         print(76*'-')
#         pprint(obs)
    
#     return results

# results = env.reset(agent='Red')
# obs = results.observation
# pprint(obs)
# blue_obs = env.get_observation('Blue')
# print("Blue Observation: ")
# print(list(blue_obs.keys()))

# action_space = results.action_space
# red_obs = results.observation
# print("Red Observation: ")
# print(red_obs)


# results = step_red(red_obs)
# red_obs = results.observation

# results = env.reset('Red')

def run(env, agent, agent_color, steps):
    def render_ip_to_hostname(action):
        target = ""
        if hasattr(action, 'ip_address'):
            target = env.environment_controller.state.ip_addresses[action.ip_address]
        if hasattr(action, 'hostname'):
            target = action.hostname
        return target

    print (f"Running {agent_color} Agent {agent} for {steps} steps")
    results = env.reset(agent_color)
    obs = results.observation
    action_space = results.action_space
    for i in range(steps):
        action = agent.get_action(obs,action_space)
        # results = env.step(action=action,agent='Red')
        results = env.step(action=action,agent='Blue')
        obs = results.observation
        print("Step: ", i, "---------------------------------")
    
        print(f"{action.agent} Action: {action} {render_ip_to_hostname(action)}")
        print(f"Red Action: { env.get_last_action('Red')} {render_ip_to_hostname(env.get_last_action('Red'))}")

        print('Reward: ', results.reward)
        # print(obs)

        true_state = env.get_agent_state('True')
        true_table = true_obs_to_table(true_state, env)

        print(true_table)

        # print(env.get_observation('Blue'))
        if results.done or (env.get_last_action('Red').name == 'Impact'
                             and env.get_observation('Red')['success'] == True):
                print("Done")
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run CybORG')
    parser.add_argument("-s", '--steps', type=int, default=100,
                        help='Number of steps to run')
    parser.add_argument("-b", "--blue_agent", help="BlueAgent class", default="BlueReactRemoveAgent")
    parser.add_argument("-r", "--red_agent", help="RedAgent class", default="RedMeanderAgent")

    args = parser.parse_args()


    path = inspect.getfile(CybORG)
    path = dirname(path) + f'/Simulator/Scenarios/scenario_files/Scenario1b.yaml'
    sg = FileReaderScenarioGenerator(path)

    # create blue agent, the name of the class is in args.blue_agent
    blue_agent_class = getattr(sys.modules[__name__], args.blue_agent)
    blue_agent = blue_agent_class()

    # create red agent, the name of the class is in args.red_agent
    red_agent_class = getattr(sys.modules[__name__], args.red_agent)
    red_agent = red_agent_class()

    env = CybORG(sg, agents={'Red':red_agent})
    run(env, blue_agent, 'Blue', args.steps)
