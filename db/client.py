from elasticsearch import Elasticsearch
from core import utils

ip = utils.get_config("elasticsearch", "ip")
port = utils.get_config("elasticsearch", "port")
user = utils.get_config("elasticsearch", "user")
password = utils.get_config("elasticsearch", "password")

es = Elasticsearch(f"http://{ip}:{port}", http_auth=(user, password))
