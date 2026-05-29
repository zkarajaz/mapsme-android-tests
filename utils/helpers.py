from appium.webdriver.webdriver import WebDriver
import logging

logger = logging.getLogger(__name__)

def switch_to_webview(driver: WebDriver):
    """Переключает Appium драйвер на WebView для взаимодействия с экраном оплаты"""
    contexts = driver.contexts
    logger.info(f"Доступные контексты: {contexts}")
    
    webview_context = next((c for c in contexts if 'WEBVIEW' in c), None)
    if webview_context:
        driver.switch_to.context(webview_context)
        logger.info(f"Успешно переключились на {webview_context}")
    else:
        raise Exception("WebView контекст не найден. Убедись, что WebView включен в билде МП.")

def switch_to_native(driver: WebDriver):
    driver.switch_to.context('NATIVE_APP')