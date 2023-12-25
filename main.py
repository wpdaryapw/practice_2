import os
import requests
import pytest
import logging
from faker import Faker

log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, 'logs.log')

def configure_logger(name, log_file):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger

base_logger = configure_logger('base_request_logger', log_file)


fake = Faker()

class BaseRequest:
    def __init__(self, base_url):
        self.base_url = base_url
        self.logger = base_logger

    def _request(self, url, request_type, data=None, expected_error=False):
        stop_flag = False
        while not stop_flag:
            if request_type == 'GET':
                self.logger.debug(f'Отправка GET запроса на: {url}')
                response = requests.get(url)
                stop_flag = True
            elif request_type == 'POST':
                self.logger.debug(f'Отправка POST запроса на: {url}')
                response = requests.post(url, data=data)
                stop_flag = True
            elif request_type == 'PUT':
                self.logger.debug(f'Отправка PUT запроса на: {url}')
                response = requests.put(url, data=data)
            else:
                self.logger.debug(f'Отправка DELETE запроса на: {url}')
                response = requests.delete(url)

            if not expected_error and response.status_code == 200:
                stop_flag = True
            elif expected_error:
                stop_flag = True

        self.logger.debug(f'Пример {request_type} запроса')
        self.logger.debug(response.url)
        self.logger.debug(f'Код состояния: {response.status_code}')
        self.logger.debug(f'Причина: {response.reason}')
        self.logger.debug(f'Текст ответа: {response.text}')
        self.logger.debug(f'JSON ответа: {response.json()}')
        self.logger.debug('**********')
        return response

    def get(self, endpoint, endpoint_id, expected_error=False):
        url = f'{self.base_url}/{endpoint}/{endpoint_id}'
        response = self._request(url, 'GET', expected_error=expected_error)
        return response.json()

    def post(self, endpoint, body):
        url = f'{self.base_url}/{endpoint}/'
        response = self._request(url, 'POST', data=body)
        return response.status_code

    def delete(self, endpoint, endpoint_id):
        url = f'{self.base_url}/{endpoint}/{endpoint_id}'
        response = self._request(url, 'DELETE')
        return response.status_code

    def put(self, endpoint, endpoint_id, body):
        url = f'{self.base_url}/{endpoint}/{endpoint_id}'
        response = self._request(url, 'PUT', data=body)
        return response.status_code

    def get_user(self, endpoint_id, expected_error=False):
        url = f'{self.base_url}/users/{endpoint_id}'
        response = self._request(url, 'GET', expected_error=expected_error)
        return response.json()

    def create_user(self):
        data = {
            'name': fake.name(),
            'username': fake.user_name(),
            'email': fake.email()
        }
        return self.post('users', data)

    def update_user(self, user_id):
        data = {
            'name': fake.name(),
            'username': fake.user_name(),
            'email': fake.email()
        }
        return self.put('users', user_id, data)

    def delete_user(self, user_id):
        return self.delete('users', user_id)


BASE_URL = 'http://localhost:3000'

base_request = BaseRequest(BASE_URL)

@pytest.mark.parametrize('i', range(1,2))
def test_create_user(i):
    test_new = base_request.create_user()
    assert test_new == 201
    base_request.logger.debug(f'Создан пользователь: {i + 1}')

@pytest.mark.parametrize('id', range(55,56))
def test_update_user(id):
    user_details = base_request.get('users', 4)
    test_update = base_request.update_user(id)
    assert test_update == 200
    base_request.logger.debug(f'Обновлен пользователь с ID {id}')

def test_delete_last_user():
    all_users = base_request.get('users', '')

    num_users = len(all_users)

    if num_users > 0:
        last_user_id = all_users[-1]['id']
        deleted = base_request.delete_user(last_user_id)
        assert deleted == 200
        base_request.logger.debug(f'Удален пользователь с ID {last_user_id}')
    else:
        base_request.logger.debug('Нет пользователей для удаления')


