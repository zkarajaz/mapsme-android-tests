from api.base_client import BaseAPIClient
from config.settings import Config
from config.endpoints import Endpoints

class PaymentMethodsClient:
    def __init__(self, client: BaseAPIClient):
        self.client = client
        self.base_url = Config.SUB_URL
        
    def get_payment_methods(self):
        return self.client.get(f"{self.base_url}{Endpoints.PAYMENT_METHODS}")