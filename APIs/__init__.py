import requests
import json
from Drivers import Connections

unspecified = "unspecified"


class BaseRpcApi:
    def __init__(self, url):
        self.rpc_connection = Connections.RpcConnection(url=url)


unspecified = "unspecified"


class BaseApi:
    HEADERS = {
        "Content-Type": "application/json",
        "Connection": "keep-alive",
    }

    def __init__(self, url):
        self.base_url = url

    def post(self, path, data):
        return requests.post(f"{self.base_url}/{path}", json.dumps(data), headers=BaseApi.HEADERS)

    def get(self, path):
        return requests.get(f"{self.base_url}/{path}", headers=BaseApi.HEADERS)
