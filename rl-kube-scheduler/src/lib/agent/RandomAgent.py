import numpy as np


class RandomAgent:
    def __init__(self) -> None:
        pass

    def act(self, observation):
        return np.random.choice(range(len(observation["nodes"])))
