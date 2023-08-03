import random
import inspect
from os.path import dirname
from pprint import pprint
import argparse
import sys
from CybORG import CybORG
from CybORG.Simulator.Scenarios import FileReaderScenarioGenerator
from CybORG.Agents import B_lineAgent, KillchainAgent, RedMeanderAgent, \
    BlueReactRemoveAgent, BlueReactRestoreAgent, HeuristicRed, MonitorAgent, \
    SleepAgent, WinRedMeanderAgent, LinRedMeanderAgent, BlueLoadAgent 

from CybORG.Agents.Wrappers.TrueTableWrapper import true_obs_to_table
from CybORG.Agents.Wrappers.FixedFlatWrapper import FixedFlatWrapper
from CybORG.Agents.Wrappers import ChallengeWrapper

def run(env, agent, agent_color, steps: int, episodes: int, silent: bool = False):
    def render_ip_to_hostname(action):
        target = ""
        if hasattr(action, 'ip_address'):
            leaf_env = env
            while not hasattr(leaf_env, "environment_controller"):
                leaf_env = leaf_env.env
            target = leaf_env.environment_controller.state.ip_addresses[action.ip_address]
        if hasattr(action, 'hostname'):
            target = action.hostname
        return target

    rewards = []
    for e in range(episodes):
        step_rewards = []
        if not silent: print (f"Running {agent_color} Agent {agent} for {steps} steps")
        if type(env) == CybORG:
            results = env.reset(agent_color)
            obs = results.observation
            action_space = results.action_space
        else:
            obs = env.reset()
            action_space = env.get_action_space(agent_color)

        for i in range(steps):
            if type(env) == CybORG:
                action = agent.get_action(obs,action_space)
                # results = env.step(action=action,agent='Red')
                results = env.step(action=action,agent='Blue')
                obs = results.observation
                reward = results.reward
                done = results.done
            else:
                action = agent.get_action(obs, action_space)
                obs, reward, done, info = env.step(action)
                # a.append((str(cyborg.get_last_action('Blue')), str(cyborg.get_last_action('Red'))))
    
            if not silent: print("Step: ", i, "---------------------------------")
        
            if not silent: print(f"Blue Action: {env.get_last_action('Blue')} {render_ip_to_hostname(env.get_last_action('Blue'))}")
            if not silent: print(f"Red Action: { env.get_last_action('Red')} {render_ip_to_hostname(env.get_last_action('Red'))}")

            if not silent: print('Reward: ', reward)
            # print(obs)
            step_rewards.append(reward)

            true_state = env.get_agent_state('True')
            true_table = true_obs_to_table(true_state, env)

            if not silent: print(true_table)

            if (env.get_last_action('Red').name == 'Impact'):
                # the Red agent is not wrapped so get it's observation from the CybOrg env
                cyborg = env
                while not type(cyborg) == CybORG:
                    cyborg = cyborg.env
                if cyborg.get_observation('Red')['success'] == True:
                    done =True
            if done:
                if not silent: print("Done")
                break
        rewards.append(sum(step_rewards))
    print(f"Average reward: {sum(rewards)/len(rewards)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run CybORG')
    parser.add_argument("-e", '--episodes', type=int, default=1,
                        help='Number of episodes to run')
    parser.add_argument("-s", '--steps', type=int, default=100,
                        help='Number of steps to run')
    parser.add_argument("-b", "--blue_agent", help="BlueAgent class", default="MonitorAgent")
    parser.add_argument("-r", "--red_agent", help="RedAgent class", default="RedMeanderAgent")

    # Add a boolean argument whether to train the blue agent first
    parser.add_argument("-tb", "--train_blue", help="Train the blue agent first", action="store_true")
    parser.add_argument("-ts", '--train_steps', type=int, default=1e6,
                        help='Number of steps to train for')
    parser.add_argument("-sl", "--silent", help="No prints", action="store_true")

    args = parser.parse_args()

    path = inspect.getfile(CybORG)
    path = dirname(path) + f'/Simulator/Scenarios/scenario_files/Scenario1b.yaml'
    sg = FileReaderScenarioGenerator(path)

    # create red agent, the name of the class is in args.red_agent
    red_agent_class = getattr(sys.modules[__name__], args.red_agent)
    red_agent = red_agent_class()

    # create blue agent, the name of the class is in args.blue_agent
    blue_agent_class = getattr(sys.modules[__name__], args.blue_agent)
    blue_agent = blue_agent_class()

    env = CybORG(sg, agents={'Red':red_agent})
    if args.blue_agent == 'BlueLoadAgent':
        cyborg = ChallengeWrapper(env=env, agent_name='Blue', max_steps=args.steps)
        # train the blue agent first
        if args.train_blue:
            blue_agent.learn(args.train_steps, cyborg)
    else:
        cyborg = env


    run(cyborg, blue_agent, 'Blue', args.steps, args.episodes, args.silent)
