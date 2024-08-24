import numpy as np


class GreedyAgent:
    def __init__(self, epsilon=0.9) -> None:
        self.epsilon = epsilon

    def act(self, observation):
        p = np.random.random()
        if p > self.epsilon:
            capacities = [
                node.schedulable_cpu + node.schedulable_memory
                for node in observation["nodes"]
            ]
            action = np.argmax(capacities)
        else:
            action = np.random.choice(range(len(observation["nodes"])))
        return action
