# skitAPI.py

import requests
import base64
from requests.auth import HTTPBasicAuth
import json
from pprint import pformat

from sqlalchemy.future import select
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession


# мои модули
from vars_init import config
from middlewares.db import DataBaseSession
from database.engine import session_maker
from database.application import Application
from database.user import User
from database.engine import connection





def string_to_base64(input_string):
    bytes_input = input_string.encode('utf-8')
    base64_bytes = base64.b64encode(bytes_input)
    base64_string = base64_bytes.decode('utf-8')
    
    return base64_string


class SkitApi:
    def __init__(self):
        self.session_token = ''

    @classmethod
    @connection
    async def make_session(self, tgid: int, session: AsyncSession):
        result = await session.execute(select(User).where(User.tgid == tgid))
        user = list(result.scalars())[0]

        url = config.API_URL + 'initSession'
        headers = {
            'App-Token': config.API_TOKEN,
            'Content-Type': 'application/json',
            'Authorization': f"Basic {string_to_base64(f'{user.login}:{user.password}')}"
        }
        
        response = requests.get(url=url, headers=headers, verify=False)
        data = response.json()
        if response.status_code == 200:
            data = response.json()
            self.session_token = data['session_token']
            return True
        
        print(f"Возникла ошибка при создании сессии")
        return False
    
    @classmethod
    def kill_session(self):
        url = config.API_URL + 'killSession'
        headers = {
            'App-Token': config.API_TOKEN,
            'Content-Type': 'application/json',
            'Session-Token': self.session_token
        }

        response = requests.get(url=url, headers=headers, verify=False)
        if response.status_code == 200:
            return True
        return False
    
    @classmethod
    @connection
    async def make_application(self, name: str, content: str, tgid: int,  session):
        url = config.API_URL + 'Ticket'
        await self.make_session(tgid=tgid)
        headers = {
            'App-Token': config.API_TOKEN,
            'Content-Type': 'application/json',
            'Session-Token': self.session_token
        }

        body_data = {
            'input': {
                'name': name,
                'content': content
            }
        }

        response = requests.post(url=url, headers=headers, data=json.dumps(body_data), verify=False)
        data = response.json()
        id = data['id']

        application = Application(user_tgid=tgid, id=id)
        session.add(application)
        await session.commit()
        self.kill_session()

    @classmethod
    @connection
    async def get_applications(self, tgid: int, session: AsyncSession) -> list[str]:
        await self.make_session(tgid=tgid)
        res = []

        result = await session.execute(select(Application).where(Application.user_tgid == tgid))
        tickets: list[Application] = list(result.scalars())
        
        for ticket in tickets:
            url = config.API_URL + 'Ticket/' + str(ticket.id)

            headers = {
                'App-Token': config.API_TOKEN,
                'Content-Type': 'application/json',
                'Session-Token': self.session_token
            }

            params = {
                'expand_dropdowns': True
            }


            response = requests.get(url=url, headers=headers, params=params, verify=False)
            data = response.json()
            res += [pformat(data)]

        self.kill_session()
        return res


