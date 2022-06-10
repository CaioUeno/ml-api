import random
from typing import List


class Dummy:
    def __init__(self):
        pass

    def predict(self, texts: List[str]) -> List[int]:
        return [random.randint(-1, 1) for text in texts]


dummy = Dummy()
