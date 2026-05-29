from api.base_client import BaseAPIClient
from config.settings import Config
from config.endpoints import Endpoints

class AuthClient:
    def __init__(self, client: BaseAPIClient):
        self.client = client
        self.base_url = Config.AUTH_URL
        
    def accept_terms(self):
        return self.client.patch(f"{self.base_url}{Endpoints.ACCEPT_TERMS}")