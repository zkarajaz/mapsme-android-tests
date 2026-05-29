from api.base_client import BaseAPIClient
from config.settings import Config
from config.endpoints import Endpoints

class PurchaseClient:
    def __init__(self, client: BaseAPIClient):
        self.client = client
        self.base_url = Config.SUB_URL
        
    def purchase_new_card(self, plan_id, price_id, payload):
        endpoint = Endpoints.PURCHASE_NEW.format(plan_id=plan_id, price_id=price_id)
        return self.client.post(f"{self.base_url}{endpoint}", json=payload)

    def purchase_saved_card(self, method_id, plan_id, price_id, payload):
        endpoint = Endpoints.PURCHASE_SAVED.format(method_id=method_id, plan_id=plan_id, price_id=price_id)
        return self.client.post(f"{self.base_url}{endpoint}", json=payload)