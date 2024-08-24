#!/usr/bin/env python3
import os
import sys
import requests

from kubernetes import client, config

import gym
from gym import spaces

from environment.k8s_utils import Node, Pod

SIMULATOR_CONFIG = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "resources",
    "initial_simulator_config.yaml",
)


class K8sScheduling(gym.Env):
    def __init__(
        self,
        config_file=None,
        n_nodes=4,
        n_pods=25,
        namespace="default",
        scheduler_name="default-scheduler",
    ):
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config(config_file=config_file)

        self.n_nodes = n_nodes
        self.n_pods = n_pods + 1
        self.k8s_client = client.CoreV1Api(client.ApiClient())
        self.namespace = namespace
        self.scheduler_name = scheduler_name

    def reset(self):
        self._reset_simulator()
        self._init_simulator()
        return self.next_obs

    def close(self):
        self._reset_simulator()

    def step(self, action):
        selected_pod = next(self._events)
        selected_node = self.nodes[int(action)]
        self._schedule_pod(
            name=selected_pod.name,
            node=selected_node.name,
        )
        reward = self.reward(selected_node)
        return self.next_obs, reward, self.done, {}

    def reward(self, selected_node):
        reward = 0
        # Penalize agent with total remaining capacity on selected node
        reward -= (
            selected_node.schedulable_cpu + selected_node.schedulable_memory
        )

        # Penalize agent for pods exceeding node capacity
        # reward -= selected_node.schedulable_pods

        # Penalize agent for pods not scheduled
        # reward -= len(
        #     [pod for pod in self.pods if not pod.is_scheduled()]
        # )
        return reward

    def _reset_simulator(self):
        response = requests.put("http://localhost:1212/api/v1/reset")
        if response.status_code != 202:
            print(
                "Error {} while resetting simulator {}".format(
                    response.status_code, response.text
                )
            )
            sys.exit(1)

    def _init_simulator(self):
        for _ in range(self.n_nodes):
            self._create_node()

    @property
    def action_space(self):
        return spaces.Discrete(self.n_nodes)

    @property
    def observation_space(self):
        pass

    @property
    def done(self):
        return len(self.pods) >= self.n_pods

    @property
    def next_obs(self):
        self._create_pod()
        self.state = {"nodes": self.nodes, "pods": self.pods}
        return self.state

    @property
    def _events(self):
        for pod in self.pods:
            if not pod.is_scheduled():
                yield pod

    @property
    def nodes(self):
        return [Node(node, self.pods) for node in self.k8s_client.list_node().items]

    @property
    def pods(self):
        return [
            Pod(pod)
            for pod in self.k8s_client.list_namespaced_pod(self.namespace).items
            if pod.spec.scheduler_name == self.scheduler_name
        ]

    def _create_node(self, node_name="node-"):
        node_manifest = {
            "apiVersion": "v1",
            "kind": "Node",
            "metadata": {"generateName": node_name},
            "status": {
                "capacity": {
                    "cpu": "4",
                    "memory": "32Gi",
                    "pods": "110",
                },
                "allocatable": {
                    "cpu": "4",
                    "memory": "32Gi",
                    "pods": "110",
                },
                "phase": "Running",
                "conditions": [{"type": "Ready", "status": "True"}],
            },
        }
        return self.k8s_client.create_node(node_manifest)

    def _create_pod(
        self,
        pod_name="pod-",
        container_name="container",
        container_image="image",
        restart_policy="Never",
        env_vars=[],
    ):
        dict_env_vars = [{"name": row[0], "value": row[1]} for row in env_vars]
        pod_manifest = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"generateName": pod_name},
            "spec": {
                "schedulerName": self.scheduler_name,
                "containers": [
                    {
                        "image": container_image,
                        "name": container_name,
                        "env": dict_env_vars,
                        "resources": {
                            "limits": {"cpu": "500m", "memory": "1Gi"},
                            "requests": {"cpu": "250m", "memory": "256Mi"},
                        },
                    }
                ],
                "restartPolicy": restart_policy,
            },
        }
        return self.k8s_client.create_namespaced_pod(self.namespace, pod_manifest)

    def _schedule_pod(self, name, node):
        body = client.V1Binding(
            metadata=client.V1ObjectMeta(name=name),
            target=client.V1ObjectReference(name=node, kind="Node", api_version="v1"),
        )
        # print("Scheduling pod {} on node {}".format(name, node))
        return self.k8s_client.create_namespaced_pod_binding(
            name, self.namespace, body, _preload_content=False
        )
