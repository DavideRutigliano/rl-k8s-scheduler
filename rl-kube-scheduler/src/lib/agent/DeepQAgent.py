import os
from stable_baselines3 import DQN
from stable_baselines3.common.callbacks import EvalCallback

from stable_baselines3.common.env_checker import check_env


class DeepQAgent:
    def __init__(self, env, eval_env=None, load=False, filename="deepq-scheduler.model") -> None:
        self._env = env
        self._eval_env = eval_env
        check_env(self._env)
        if self._eval_env:
            check_env(self._eval_env)
        self.filename = filename
        self.policy = "MultiInputPolicy"
        self.model = DQN(policy=self.policy, env=self._env, verbose=1)
        if load:
            self.load()

    def train(self, steps=1000):
        args = {}
        if self._eval_env:
            args["callback"] = EvalCallback(
                self._eval_env,
                eval_freq=steps//5,
                deterministic=True,
                render=False,
            )
        self.model = self.model.learn(total_timesteps=steps, **args)
        self.model.save(self.filename)

    def load(self):
        if os.path.isfile(self.filename):
            self.model.set_parameters(self.filename)

    def act(self, observation):
        assert self.model
        action, _ = self.model.predict(observation, deterministic=True)
        return action
