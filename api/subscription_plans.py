from api.base_client import BaseAPIClient
from config.settings import Config
from config.endpoints import Endpoints

class SubscriptionPlansClient:
    def __init__(self, client: BaseAPIClient):
        self.client = client
        self.base_url = Config.BASE_URL # URL отличается в доке и в коде, нужно уточнить
        
    def get_plans(self, params=None):
        return self.client.get(f"{self.base_url}{Endpoints.SUB_PLANS}", params=params)