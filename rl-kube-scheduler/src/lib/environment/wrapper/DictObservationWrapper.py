import numpy as np

import gym
from gym import spaces


class DictObservationWrapper(gym.ObservationWrapper):
    def __init__(self, env):
        super().__init__(env)

    @property
    def observation_space(self):
        return spaces.Dict(
            {
                "nodes": spaces.Box(low=0, high=np.inf, shape=(self.n_nodes, 3)),
                "pods": spaces.Box(low=0, high=np.inf, shape=(self.n_pods, 2)),
            }
        )
        # return spaces.Graph(
        #     node_space=spaces.Box(low=0, high=len(self.pods), shape=(5,)),
        #     edge_space=spaces.Box(low=0, high=self.n_nodes, shape=(4, ))
        # )

    def reset(self, **kwargs):
        observation = self.env.reset(**kwargs)
        return self.observation(observation)

    def step(self, action):
        observation, reward, done, info = self.env.step(action)
        return self.observation(observation), reward, done, info

    def observation(self, observation):
        nodes = np.zeros((self.n_nodes, 3), dtype=np.float32)
        for i, node in enumerate(observation["nodes"]):
            nodes[i] = [
                node.schedulable_pods,
                node.schedulable_cpu,
                node.schedulable_memory,
            ]
        pods = np.zeros((self.n_pods, 2), dtype=np.float32)
        for i, pod in enumerate(observation["pods"]):
            pods[i] = [
                pod.cpu_requests,
                pod.mem_requests,
            ]
        return {
            "nodes": nodes.reshape((self.n_nodes, 3)),
            "pods": pods.reshape((self.n_pods, 2)),
        }
        # encoded = np.eye(len(state["pods"]), len(state["nodes"]), k=0, dtype=np.int32)
        # for i, pod in enumerate(state["pods"]):
        #     for j, node in enumerate(state["nodes"]):
        #         if node["name"] == pod["node"]:
        #             encoded[i][j] = 1
        # return encoded
