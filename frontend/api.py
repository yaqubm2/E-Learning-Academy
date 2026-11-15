"""Simple JSON client for the local FastAPI service."""
import os
import requests

BASE_URL=os.getenv('ACADEMY_API_URL','http://127.0.0.1:8000').rstrip('/')
class ApiError(Exception): pass

class AcademyAPI:
    def __init__(self):
        self.token=None
        self.role=None
        self.session=requests.Session()

    def call(self,method,path,payload=None):
        headers={'Authorization':f'Bearer {self.token}'} if self.token else {}
        try:
            response=self.session.request(method,BASE_URL+path,json=payload,headers=headers,timeout=15)
            if not response.ok:
                try:
                    detail=response.json().get('detail',response.text)
                    if isinstance(detail,list):
                        detail='; '.join(str(x.get('msg','Invalid input')) for x in detail)
                except ValueError:
                    detail=response.text
                raise ApiError(str(detail))
            return response.json()
        except requests.RequestException as exc:
            raise ApiError(f'Cannot reach backend at {BASE_URL}. Run FastAPI first. {exc}') from exc

    def authenticate(self,path,data):
        response=self.call('POST',path,data)
        self.token=response['access_token']
        self.role=response['role']
        return self.call('GET','/auth/me')['account']

    def logout(self):
        if self.token:
            try: self.call('POST','/auth/logout')
            except ApiError: pass
        self.token=None
        self.role=None
