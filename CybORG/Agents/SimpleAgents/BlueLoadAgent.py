import inspect
import os
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import ProgressBarCallback

# from CybORG import CybORG
from CybORG.Agents.SimpleAgents.BaseAgent import BaseAgent
# from CybORG.Agents.Wrappers.EnumActionWrapper import EnumActionWrapper
# from CybORG.Agents.Wrappers.FixedFlatWrapper import FixedFlatWrapper
# from CybORG.Agents.Wrappers.OpenAIGymWrapper import OpenAIGymWrapper

# from CybORG.Agents.Wrappers import ChallengeWrapper

class BlueLoadAgent(BaseAgent):
    # agent that loads a StableBaselines3 PPO model file
    def train(self, results):
        pass

    def end_episode(self):
        pass

    def set_initial_values(self, action_space, observation):
        pass

    def __init__(self, model_file: str = None):
        if model_file is not None:
            self.model = PPO.load(model_file)
        else:
            self.model = None
            if os.path.exists("blue_load_mlp.zip"):
                self.model = PPO.load("blue_load_mlp")

    def get_action(self, observation, action_space):
        """gets an action from the agent that should be performed based on the agent's internal state and provided observation and action space"""
        if self.model is None:
            self.logger.error("No model loaded")
            return None
            # path = str(inspect.getfile(CybORG))
            # path = path[:-7] + f'/Shared/Scenarios/Scenario1b.yaml'
            # cyborg = ChallengeWrapper(env=CybORG(path, 'sim'), agent_name='Blue')
            # self.model = PPO('MlpPolicy', cyborg)
        action, _states = self.model.predict(observation)
        return action

    def learn(self, steps, env):
        if self.model is None:
            self.model = PPO('MlpPolicy', env, policy_kwargs={"net_arch":[256,256]})
            self.model.learn(total_timesteps=steps, callback=ProgressBarCallback())
            self.model.save("blue_load_mlp")  # save model
