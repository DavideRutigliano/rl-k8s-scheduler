import gym


class NoOpWrapper(gym.Wrapper):
    def __init__(self, env):
        super().__init__(env)

    @property
    def _events(self):
        yield self.env.pods[-1]

    def step(self, _):
        terminated = False
        selected_pod = next(self._events)
        selected_node = [
            node for node in self.env.nodes if node.name == selected_pod.node
        ][0]
        reward = self.env.reward(selected_node)
        return self.env.next_obs, reward, terminated, None
