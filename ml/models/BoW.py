import pickle

from core import utils

bow = pickle.load(open(utils.get_config("ml", "model_filename"), "rb"))
