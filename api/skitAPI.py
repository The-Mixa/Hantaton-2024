import requests
import base64
from requests.auth import HTTPBasicAuth
import json

from sqlalchemy.future import select
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Tuple, Dict

# мои модули
from vars_init import config
from middlewares.db import DataBaseSession
from database.engine import session_maker
from database.application import Application, statuses
from database.user import User
from database.engine import connection


def string_to_base64(input_string):
    bytes_input = input_string.encode('utf-8')
    base64_bytes = base64.b64encode(bytes_input)
    base64_string = base64_bytes.decode('utf-8')

    return base64_string


async def application_message_format(data: dict) -> str:
    answer = (f"<b>Заявка №{data['id']}</b>\n"
            f"Имя заявки: <b>{data['name']}</b>\n"
            f"Статус заявки: <b>{statuses.enscriptons[data['status']]}</b>\n"
            f"Дата создания: <b>{data['date_creation']}</b>\n\n"
            f"Содержание заявки:\n"
            f"{data['content']}")
    
    answer = answer.replace('&lt;br&gt;', '\n')
    answer = answer.replace('&lt;/p&gt;', '')
    answer = answer.replace('&lt;p&gt;', '')
    
    return answer

async def application_solution_format(tgid: int, data: dict) -> str:
    answer = ''
    links = data['links']
    for link in links:
        if link['rel'] == 'ITILSolution':
            answer = await api.get_application_solution(tgid, link['href'])
            break
            
    answer =  (f"<b>Получен ответ на заявку №{data['id']}</b>\n"
            f"Имя заявки: <b>{data['name']}</b>\n"
            f"Содержание заявки:\n"
            f"{data['content']}\n\n"
            f"Ответ на заявку:\n"
            f"{answer}")
    
    answer = answer.replace('&lt;br&gt;', '\n')
    answer = answer.replace('&lt;/p&gt;', '')
    answer = answer.replace('&lt;p&gt;', '')
        
    return answer


class SkitApi:
    def __init__(self):
        self.session_token = ''

    @classmethod 
    @connection
    async def make_session(self, tgid: int, session: AsyncSession) -> bool:
        tgid = str(tgid)  # Приводим tgid к строке
        result = await session.execute(select(User).where(User.tgid == tgid))
        user = list(result.scalars())[0]

        url = config.API_URL + 'initSession'
        headers = {
            'App-Token': config.API_TOKEN,
            'Content-Type': 'application/json',
            'Authorization': f"Basic {string_to_base64(f'{user.login}:{user.password}')} "
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
    def kill_session(self) -> bool:
        url = config.API_URL + 'killSession'
        headers = {
            'App-Token': config.API_TOKEN,
            'Content-Type': 'application/json',
            'Session-Token': self.session_token
        }

        response = requests.get(url=url, headers=headers, verify=False)
        if response.status_code == 200:
            self.session_token = ''
            return True
        return False

    @classmethod
    @connection
    async def make_application(self, name: str, content: str, tgid: int, session) -> None:
        tgid = str(tgid)  # Приводим tgid к строке
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
    async def get_applications(self, tgid: int, session: AsyncSession, archive=False) -> List[Tuple[(str, int)]]:
        tgid = str(tgid)  # Приводим tgid к строке
        await self.make_session(tgid=tgid)
        res = []

        result = await session.execute(select(Application).where(Application.user_tgid == tgid))
        tickets: List[Application] = list(result.scalars())

        for ticket in tickets:
            if archive:
                if ticket.status >= 5:
                    continue
            else:
                if ticket.status < 5:
                    continue

            # Отправляем запрос к внешнему API для получения информации о заявке
            url = config.API_URL + 'Ticket/' + str(ticket.id)
            headers = {
                'App-Token': config.API_TOKEN,
                'Content-Type': 'application/json',
                'Session-Token': self.session_token
            }

            response = requests.get(url=url, headers=headers, verify=False)
            if response.status_code == 200:
                data = response.json()
                res += [(data['name'], data['id'])]
            else:
                print(f"API request failed for ticket ID {ticket.id} with status code {response.status_code}")

        self.kill_session()
        return res


    @classmethod
    @connection
    async def get_application(self, id: int, session: AsyncSession) -> dict:
        tickets_result = await session.execute(select(Application).where(Application.id == id))
        tickets: List[Application] = list(tickets_result.scalars())
        if not tickets:
            return "Заявка не найдена"
        ticket = tickets[0]
        await self.make_session(ticket.user_tgid)

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

        return data

    @classmethod
    async def get_application_by_id(self, id: int) -> str:
        data = await self.get_application(id)
        return await application_message_format(data)


    @classmethod
    @connection
    async def get_all_users(self, session: AsyncSession) -> List[Tuple[str, str]]:
        # Выполнение запроса к базе данных для получения всех пользователей
        users_result = await session.execute(select(User))
        users: list[User] = list(users_result.scalars())

        # Возвращаем список кортежей (login, tgid)
        return [(user.login, user.tgid) for user in users]

    @classmethod
    @connection
    async def get_all_applications(self, session: AsyncSession) -> list[(str, str)]:
        applications_result = await session.execute(select(Application))
        applications: list[Application] = list(applications_result.scalars())

        res = []
        for application in applications:
            user_result = await session.execute(select(User).where(User.tgid == application.user_tgid))
            user: User = list(user_result.scalars())[0]
            data = await self.get_application(application.id)

            res += [(data['name'], user.login)]

        return res
    
    
    @classmethod
    async def get_application_solution(self, tgid: int, url: str) -> str:
        await self.make_session(tgid=tgid)

        headers = {
            'App-Token': config.API_TOKEN,
            'Content-Type': 'application/json',
            'Session-Token': self.session_token
        }

        response = requests.get(url=url, headers=headers, verify=False)
        if response.status_code == 200:
            data = response.json()
            if not data:
                return 'Решение не указано'
            print(data)
            print(response.request.url)
            return data[0]['content']
        else:
            print(f"API request failed for ticket with status code {response.status_code}")

        self.kill_session()
        return 'Решение не указано'


api = SkitApi()
