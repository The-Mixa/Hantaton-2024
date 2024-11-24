# skitAPI.py

import requests
import base64
import json

# мои модули
from vars_init import config


def string_to_base64(input_string):
    bytes_input = input_string.encode('utf-8')
    base64_bytes = base64.b64encode(bytes_input)
    base64_string = base64_bytes.decode('utf-8')
    
    return base64_string


class SkitApi:
    def __init__(self) -> None:
        url = config.API_URL + 'initSession'
        headers = {
            'App-Token': config.API_TOKEN,
            'Content-Type': 'application/json',
            'Autorization': f"Basic {string_to_base64(f'{config.API_LOGIN}:{config.API_PASSWORD}')}"
        }
        
        print(headers)
        request = requests.get(url=url, headers=headers)
        data = json.loads(request.text)
        
        try:
            self.session_token = data['session_token']
        except Exception as e:
            print(f"Возникла ошибка при создании сессии: {e}")

    


SkitApi()

