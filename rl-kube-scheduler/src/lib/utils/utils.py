import os
import yaml
import random
import numpy as np
import torch


def read_yaml_file(filename):
    with open(filename, "r") as file:
        return yaml.safe_load(file.read())


def random_seed(seed=2023):
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)


def seed_torch(seed=2023):
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def seed_everything(seed=2023):
    random_seed(seed)
    seed_torch(seed)
