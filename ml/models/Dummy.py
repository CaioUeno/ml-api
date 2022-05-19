import random
import numpy as np


class Dummy:
    def __init__(self, n_classes: int = 2):
        self.n_classes = n_classes

    def single_prediction(self, text: str) -> int:
        return random.randint(-1, 1)
