from api.base_client import BaseAPIClient
from config.settings import Config
from config.endpoints import Endpoints

class UserDetailsClient:
    def __init__(self, client: BaseAPIClient):
        self.client = client
        self.base_url = Config.AUTH_URL
        
    def get_user_details(self):
        return self.client.get(f"{self.base_url}{Endpoints.USER_DETAILS}")