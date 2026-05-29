from appium.webdriver.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def switch_to_webview(self):
        """Хелпер для переключения в WebView ЮКассы"""
        contexts = self.driver.contexts
        webview = next((c for c in contexts if 'WEBVIEW' in c), None)
        if webview:
            self.driver.switch_to.context(webview)

    def switch_to_native(self):
        self.driver.switch_to.context('NATIVE_APP')