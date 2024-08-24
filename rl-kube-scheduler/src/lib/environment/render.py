import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt


def plot_reward(data):
    data = pd.DataFrame(data)
    plt.figure(figsize=(10, 7))
    plt.title("Agent Reward per Episode")
    plt.cla()
    sns.lineplot(data=data, x="Episode", y="Reward", hue="Agent")
    lims = plt.xlim()
    plt.xlim(lims)
    plt.tight_layout()
    plt.savefig("reward.png")
