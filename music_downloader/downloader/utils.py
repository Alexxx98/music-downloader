import requests
import json


def get_api_data(url, token):
    header = {"Authorization": "Bearer " + token}
    response = requests.get(url, headers=header)
    return json.loads(response.content)
