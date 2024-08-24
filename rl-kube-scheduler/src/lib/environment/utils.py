from gym.envs.registration import register


def register_env():
    register(
        id="K8sScheduling-v0",
        entry_point="environment.K8sScheduling:K8sScheduling",
        # disable_env_checker=True
    )
