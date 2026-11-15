"""HTTP client: the Flet app talks to the separately running FastAPI service."""
import os
import requests

BASE_URL = os.getenv('ACADEMY_API_URL','http://127.0.0.1:8000').rstrip('/')

class ApiError(Exception): pass

class AcademyAPI:
    def __init__(self):
        self.token = None
        self.session = requests.Session()
    def call(self, method, path, payload=None, admin=False):
        headers = {'Authorization':f'Bearer {self.token}'} if admin and self.token else {}
        try:
            res = self.session.request(method,BASE_URL+path,json=payload,headers=headers,timeout=12)
            if not res.ok:
                try: message = res.json().get('detail',res.text)
                except ValueError: message = res.text
                raise ApiError(str(message))
            return res.json()
        except requests.RequestException as exc:
            raise ApiError(f'Cannot reach API at {BASE_URL}. Start the backend first. ({exc})') from exc
    def login(self,pin):
        self.token = self.call('POST','/parent/login',{'pin':pin})['access_token']
