import requests
import urllib3
import logging
from config.settings import Config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger(__name__)

class BaseAPIClient:
    def __init__(self, jwt_token: str):
        self.session = requests.Session()
        self.session.verify = False 
        
        # Добавляем заголовки устройства, которые требует бэкенд для подписок
        self.session.headers.update({
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json",
            "X-Country-Iso-2-Code": "RU",
            "X-Device-Id": "automation_device_id_123",           # Добавлено
            "X-Device-Fingerprint": "automation_fingerprint_456"  # Добавлено
        })
        self.base_url = Config.BASE_URL
        
    def _build_url(self, url: str) -> str:
        if url.startswith("http://") or url.startswith("https://"):
            return url
        return f"{self.base_url}{url}"
    
    def get(self, url: str, **kwargs) -> requests.Response:
        full_url = self._build_url(url)
        logger.debug(f"GET {full_url}")
        return self.session.get(full_url, timeout=Config.TIMEOUT, **kwargs)
    
    def post(self, url: str, json=None, **kwargs) -> requests.Response:
        full_url = self._build_url(url)
        logger.debug(f"POST {full_url} | body={json}")
        return self.session.post(full_url, json=json, timeout=Config.TIMEOUT, **kwargs)
    
    def patch(self, url: str, json=None, **kwargs) -> requests.Response:
        full_url = self._build_url(url)
        logger.debug(f"PATCH {full_url} | body={json}")
        return self.session.patch(full_url, json=json, timeout=Config.TIMEOUT, **kwargs)