import os

from pint import UnitRegistry


UNITS_REGISTRY = UnitRegistry()
UNITS_REGISTRY.load_definitions(
    os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "resources",
        "k8s_units.txt",
    )
)
Q_ = UNITS_REGISTRY.Quantity


class Node:
    def __init__(self, node, pods):
        self._node = node
        self._get_info(pods)

    def _get_info(self, pods):
        self.name = self._node.metadata.name
        allocatable = self._node.status.allocatable
        self.max_pods = int(allocatable["pods"])
        self.cpu_alloc = Q_(allocatable["cpu"]).to("G").magnitude
        self.mem_alloc = Q_(allocatable["memory"]).to("Gi").magnitude
        self.pods = [
            pod
            for pod in pods
            if pod.node == self.name
        ]

    @property
    def schedulable_pods(self):
        return self.max_pods - len(self.pods)

    @property
    def schedulable_cpu(self):
        return self.cpu_alloc - sum(pod.cpu_requests for pod in self.pods)

    @property
    def schedulable_memory(self):
        return self.mem_alloc - sum(pod.mem_requests for pod in self.pods)

    def is_ready(self):
        if self._node.status.conditions:
            for condition in self._node.status.conditions:
                if condition.type == "Ready":
                    return condition.status == "True"
        return False


class Pod:
    def __init__(self, pod):
        self._pod = pod
        self._get_info()

    def _get_info(self):
        self.name = self._pod.metadata.name
        self.node = self._pod.spec.node_name
        cpurequests, cpulimits, memrequests, memlimits = [], [], [], []
        for container in self._pod.spec.containers:
            requests = container.resources.requests
            limits = container.resources.limits
            cpurequests.append(Q_(requests["cpu"]).to("G").magnitude)
            memrequests.append(Q_(requests["memory"]).to("Gi").magnitude)
            cpulimits.append(Q_(limits["cpu"]).to("G").magnitude)
            memlimits.append(Q_(limits["memory"]).to("Gi").magnitude)
        self.cpu_requests = sum(cpurequests)
        self.mem_requests = sum(memrequests)
        # self.cpu_limits = sum(cpulimits)
        # self.mem_limits = sum(memlimits)

    def is_scheduled(self):
        if self._pod.status.conditions:
            for condition in self._pod.status.conditions:
                if condition.type == "PodScheduled":
                    return condition.status == "True"
        return False
