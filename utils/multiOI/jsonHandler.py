import requests
import json

from constants import SamcoVariable

class JSONHandler:
    def __init__(self):
        self.filename = "option_chain.json"
        self.isLoggedIn = False

    def login(self):
        if not self.isLoggedIn:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
                }
            requestBody = {
                "userId": SamcoVariable.username,
                "password": SamcoVariable.password,
                "yob": SamcoVariable.yob
            }

            r = requests.post(SamcoVariable.apiLoginURL,
            data = json.dumps(requestBody),
            headers=headers)

            resp = r.json()
            print(resp['sessionToken'])


    def get_OC_json(self, index_name):
        headers = {"User-Agent": "Mozilla/5.0"}
