import time
import pytest
from api.base_client import BaseAPIClient
from config.settings import Config, Endpoints

APPIUM_URL = "http://127.0.0.1:4723"
APP_PACKAGE = "com.mapswithme.maps.pro"
APP_ACTIVITY = ".DefaultIcon"


@pytest.fixture(scope="module")
def driver():
    from appium.options.android.uiautomator2.base import UiAutomator2Options
    from appium.webdriver.webdriver import WebDriver
    from appium.webdriver.common.appiumby import AppiumBy
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import NoSuchElementException, TimeoutException

    opts = UiAutomator2Options()
    opts.platform_name = "Android"
    opts.device_name = "emulator-5554"
    opts.app_package = APP_PACKAGE
    opts.app_activity = APP_ACTIVITY
    opts.automation_name = "UiAutomator2"
    opts.no_reset = True
    opts.full_reset = False
    opts.new_command_timeout = 120

    d = WebDriver(APPIUM_URL, options=opts)

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _by_text(text):
        return (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")')

    def _quick(text, timeout=2):
        try:
            WebDriverWait(d, timeout).until(EC.presence_of_element_located(_by_text(text)))
            return True
        except Exception:
            return False

    def _on_subs():
        return _quick("Завершить оплату") or _quick("Выбрать другой тариф")

    def _click_text(text, timeout=5):
        try:
            WebDriverWait(d, timeout).until(EC.presence_of_element_located(_by_text(text)))
            d.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                           f'new UiSelector().text("{text}")').click()
            return True
        except Exception:
            return False

    def _exit_webview():
        """Нажать back_button несколько раз, выходя из WebView на экран карты."""
        for _ in range(5):
            try:
                d.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                               'new UiSelector().resourceId("back_button")').click()
                time.sleep(2)
            except Exception:
                break

    def _create_initiated_subscription():
        """
        More → Get PRO → Continue → Выбрать способ оплаты →
        Перейти к оплате → заполнить тестовую карту.
        Создаёт INITIATED-подписку с валидным paymentOrderPaymentConfirmationUrl.
        """
        card_number = Config.TEST_CARD_NUMBER
        card_expiry = Config.TEST_CARD_EXPIRY
        card_cvc    = Config.TEST_CARD_CVC
        if not card_number:
            return False

        _exit_webview()
        time.sleep(1)

        if not _click_text("More", timeout=10):
            return False
        time.sleep(1)

        if not _click_text("Get PRO", timeout=5):
            return False
        time.sleep(2)

        if not _click_text("Continue", timeout=5):
            return False
        time.sleep(3)

        if not _click_text("Выбрать способ оплаты", timeout=15):
            return False
        time.sleep(2)

        if not _click_text("Перейти к оплате", timeout=5):
            return False
        time.sleep(3)

        # Заполнить форму YooMoney
        try:
            fields = WebDriverWait(d, 15).until(
                lambda drv: drv.find_elements(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    'new UiSelector().className("android.widget.EditText")'
                ) or None
            )
            if not fields or len(fields) < 3:
                return False
            fields[0].click(); fields[0].send_keys(card_number); time.sleep(0.5)
            fields[1].click(); fields[1].send_keys(card_expiry); time.sleep(0.5)
            fields[2].click(); fields[2].send_keys(card_cvc);    time.sleep(0.5)
        except Exception:
            return False

        # Кнопка Pay (текст зависит от локали)
        for pay_text in ["Pay ₽ 1,799", "Оплатить", "Pay"]:
            if _click_text(pay_text, timeout=3):
                break

        time.sleep(4)

        # Нажать back_button, возвращаясь к management-экрану
        for _ in range(5):
            if _on_subs():
                return True
            try:
                d.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                               'new UiSelector().resourceId("back_button")').click()
                time.sleep(3)
            except Exception:
                break

        try:
            WebDriverWait(d, 30).until(lambda _: _on_subs())
            return True
        except TimeoutException:
            return False

    # ── Навигация к экрану подписок ─────────────────────────────────────────

    # Шаг 1: быстрый путь
    if not _on_subs():
        # Шаг 2: back_button (SPA-история)
        for _ in range(5):
            try:
                d.find_element(
                    AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("back_button")'
                ).click()
                time.sleep(3)
            except (NoSuchElementException, Exception):
                break
            if _on_subs():
                break

    if not _on_subs():
        # Шаг 3: холодный рестарт + "Complete payment"
        d.terminate_app(APP_PACKAGE)
        time.sleep(1)
        d.activate_app(APP_PACKAGE)
        if _quick("Complete payment", 30):
            d.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                           'new UiSelector().text("Complete payment")').click()
        try:
            WebDriverWait(d, 30).until(lambda _: _on_subs())
        except TimeoutException:
            pass

    if not _on_subs():
        # Шаг 4: More → Get PRO → тестовая карта → создаём новую INITIATED-подписку
        _create_initiated_subscription()
        try:
            WebDriverWait(d, 20).until(lambda _: _on_subs())
        except TimeoutException:
            pass

    yield d

    # Teardown: вернуться на экран подписок (warm WebView для следующего запуска)
    for _ in range(4):
        if _on_subs():
            break
        try:
            d.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("back_button")'
            ).click()
            time.sleep(2)
        except Exception:
            break

    d.quit()


@pytest.fixture(scope="session")
def auth_client():
    """Авторизованный HTTP-клиент (токен из .env). Живёт всю сессию."""
    return BaseAPIClient(jwt_token=Config.TEST_USER_JWT)


@pytest.fixture(scope="session")
def user_details(auth_client):
    """Кэшированный ответ GET /user_details — один запрос на всю сессию."""
    response = auth_client.get(Endpoints.USER_DETAILS)
    assert response.status_code == 200, (
        f"Не удалось получить user_details: HTTP {response.status_code} — {response.text}"
    )
    return response.json()


@pytest.fixture(scope="session")
def subscriptions_content(auth_client):
    """Кэшированный список подписок пользователя (content-массив)."""
    response = auth_client.get(Endpoints.SUBSCRIPTIONS)
    assert response.status_code == 200, (
        f"Не удалось получить подписки: HTTP {response.status_code}"
    )
    body = response.json()
    return body["page"]["content"] if "page" in body else body.get("content", [])


@pytest.fixture(scope="session")
def payment_methods_content(auth_client):
    """Кэшированный список сохранённых методов оплаты."""
    response = auth_client.get(Endpoints.PAYMENT_METHODS)
    assert response.status_code == 200, (
        f"Не удалось получить методы оплаты: HTTP {response.status_code}"
    )
    body = response.json()
    return body["page"]["content"] if "page" in body else body.get("content", [])


@pytest.fixture(scope="session")
def plans_content(auth_client):
    """Кэшированный список планов подписки."""
    response = auth_client.get(Endpoints.SUB_PLANS)
    if response.status_code != 200:
        return []
    body = response.json()
    if "page" in body:
        return body["page"].get("content", [])
    return body.get("content", [])
