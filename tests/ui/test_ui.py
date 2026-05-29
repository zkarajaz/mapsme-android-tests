import time
import pytest
import allure
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

APP_PACKAGE = "com.mapswithme.maps.pro"
WAIT = 10


def _text_present(driver, text, timeout=WAIT):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")')
            )
        )
        return True
    except (TimeoutException, NoSuchElementException):
        return False


def _find_text(driver, text, timeout=WAIT):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")')
        )
    )


def _on_subscriptions_screen(driver):
    return (
        _text_present(driver, "Завершить оплату", timeout=2)
        or _text_present(driver, "Выбрать другой тариф", timeout=2)
    )


def _dismiss_complete_payment_if_visible(driver):
    """Click 'Complete payment' bottom-sheet if it appears on the map screen."""
    if _text_present(driver, "Complete payment", timeout=3):
        try:
            driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Complete payment")'
            ).click()
            return True
        except Exception:
            pass
    return False


def _navigate_to_subscriptions(driver):
    """
    Navigate to the subscriptions management screen regardless of current state.
    1. Fast path — already there.
    2. Handle 'Complete payment' bottom-sheet on map (appears after SPA exit).
    3. Press WebView back_button (SPA history) up to 4 times.
    4. Fallback — terminate + activate → click 'Complete payment' → wait up to 45 s.
    """
    if _on_subscriptions_screen(driver):
        return

    # Step 2: handle the "Complete payment" bottom-sheet if currently on map
    if _dismiss_complete_payment_if_visible(driver):
        try:
            WebDriverWait(driver, 45).until(lambda d: _on_subscriptions_screen(d))
            if _on_subscriptions_screen(driver):
                return
        except TimeoutException:
            pass

    # Step 3: navigate back through SPA history (back_button is mapsmepro.ru SPA element)
    for _ in range(4):
        try:
            driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceId("back_button")'
            ).click()
            time.sleep(3)
        except (NoSuchElementException, Exception):
            break
        if _on_subscriptions_screen(driver):
            return
        if _dismiss_complete_payment_if_visible(driver):
            try:
                WebDriverWait(driver, 30).until(lambda d: _on_subscriptions_screen(d))
                if _on_subscriptions_screen(driver):
                    return
            except TimeoutException:
                pass

    # Step 3b: Android back key — navigates WebView history (e.g. YooMoney → mapsmepro.ru)
    for _ in range(5):
        try:
            driver.back()
            time.sleep(3)
        except Exception:
            break
        if _on_subscriptions_screen(driver):
            return
        if _dismiss_complete_payment_if_visible(driver):
            try:
                WebDriverWait(driver, 30).until(lambda d: _on_subscriptions_screen(d))
                if _on_subscriptions_screen(driver):
                    return
            except TimeoutException:
                pass

    # Step 4: cold restart
    driver.terminate_app(APP_PACKAGE)
    time.sleep(1)
    driver.activate_app(APP_PACKAGE)

    if _on_subscriptions_screen(driver):
        return

    # "Complete payment" bottom-sheet can take up to 30 s to appear after launch
    if _text_present(driver, "Complete payment", timeout=30):
        driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Complete payment")'
        ).click()

    # WebView cold-loads from API — poll up to 45 s
    try:
        WebDriverWait(driver, 45).until(lambda d: _on_subscriptions_screen(d))
    except TimeoutException:
        pass

    if not _on_subscriptions_screen(driver):
        pytest.fail(
            "Cannot reach subscriptions screen — "
            "ensure the test account has an INITIATED subscription and Appium is running."
        )


def _open_yoomoney_form(driver):
    """
    Navigate from any state to the loaded YooMoney checkout form.
    Always starts from the subscriptions screen for a clean, reproducible state.
    Waits up to 30 s for the form to fully render (detects hint='CVC' or
    content-desc 'debiting money' which are unique to the YooMoney card page).
    """
    _navigate_to_subscriptions(driver)
    _find_text(driver, "Выбрать другой тариф").click()
    time.sleep(2)
    _find_text(driver, "Выбрать способ оплаты").click()
    time.sleep(2)
    _find_text(driver, "Перейти к оплате").click()

    try:
        WebDriverWait(driver, 30).until(
            lambda d: (
                'hint="CVC"' in d.page_source
                or "debiting money" in d.page_source
                or "saving the card" in d.page_source
                or "Card number" in d.page_source
            )
        )
    except TimeoutException:
        pytest.fail("YooMoney payment form did not load within 30 s")


@allure.feature("Mobile UI: Subscription Flow")
class TestMobileUI:

    @allure.story("UI-01: Экран подписок отображает карточку INITIATED-подписки")
    def test_subscriptions_screen_shows_initiated_subscription(self, driver):
        """
        Открываем экран «Подписки».
        Проверяем заголовок «Подписки» и название продукта «MAPS.ME PRO».
        """
        _navigate_to_subscriptions(driver)

        assert _text_present(driver, "Подписки", timeout=5), (
            "Заголовок «Подписки» не найден на экране"
        )
        assert "MAPS.ME PRO" in driver.page_source, (
            "Карточка «MAPS.ME PRO» не найдена на экране подписок"
        )

    @allure.story("UI-02: INITIATED-подписка показывает статус «В процессе оплаты»")
    def test_initiated_subscription_shows_in_progress_badge(self, driver):
        """
        Карточка незавершённой подписки содержит статусный бейдж
        «В процессе оплаты».
        """
        _navigate_to_subscriptions(driver)

        assert "В процессе оплаты" in driver.page_source, (
            "Статус «В процессе оплаты» не найден в карточке подписки"
        )

    @allure.story("UI-03: Кнопка «Завершить оплату» присутствует при INITIATED-статусе")
    def test_complete_payment_button_visible_for_initiated(self, driver):
        """
        При наличии INITIATED-подписки должна отображаться кнопка
        «Завершить оплату» для продолжения незавершённого платежа.
        """
        _navigate_to_subscriptions(driver)

        btn = _find_text(driver, "Завершить оплату")
        assert btn.is_displayed(), "Кнопка «Завершить оплату» не отображается"

    @allure.story("UI-04: «Выбрать другой тариф» открывает список планов с ценами")
    def test_change_plan_shows_plan_selection_with_prices(self, driver):
        """
        Нажатие «Выбрать другой тариф» переводит на экран выбора тарифа.
        На экране видны карточки планов с ценами в рублях (символ ₽).
        """
        _navigate_to_subscriptions(driver)

        _find_text(driver, "Выбрать другой тариф").click()
        time.sleep(2)

        source = driver.page_source
        assert "MAPS.ME PRO" in source, (
            "Карточки планов подписки не найдены на экране выбора тарифа"
        )
        assert "₽" in source, (
            "Цены в рублях (символ ₽) не отображаются на экране выбора тарифа"
        )

    @allure.story("UI-05: Экран выбора оплаты показывает опцию «Оплатить новой картой»")
    def test_payment_method_selection_shows_new_card_option(self, driver):
        """
        После выбора тарифа и нажатия «Выбрать способ оплаты»
        отображается опция «Оплатить новой картой» с иконкой платёжной системы.
        """
        # Navigate to plan selection if not already there
        if not _text_present(driver, "Выбрать способ оплаты", timeout=2):
            _navigate_to_subscriptions(driver)
            _find_text(driver, "Выбрать другой тариф").click()
            time.sleep(2)

        _find_text(driver, "Выбрать способ оплаты").click()
        time.sleep(2)

        assert _text_present(driver, "Оплатить новой картой"), (
            "Опция «Оплатить новой картой» не найдена в блоке выбора способа оплаты"
        )

    @allure.story("UI-06: Блок выбора оплаты содержит активную кнопку «Перейти к оплате»")
    def test_payment_method_has_proceed_button(self, driver):
        """
        В нижнем листе выбора способа оплаты присутствует кнопка
        «Перейти к оплате», которая активна и кликабельна.
        """
        # Ensure we're on payment method selection
        if not _text_present(driver, "Перейти к оплате", timeout=2):
            _navigate_to_subscriptions(driver)
            _find_text(driver, "Выбрать другой тариф").click()
            time.sleep(2)
            _find_text(driver, "Выбрать способ оплаты").click()
            time.sleep(2)

        btn = _find_text(driver, "Перейти к оплате")
        assert btn.is_displayed(), "Кнопка «Перейти к оплате» не отображается"
        assert btn.is_enabled(), "Кнопка «Перейти к оплате» недоступна (disabled)"

    @allure.story("UI-07: Форма YooMoney содержит чекбокс согласия")
    def test_yoomoney_form_shows_agreement_checkbox(self, driver):
        """
        На форме оплаты YooMoney присутствует чекбокс / блок согласия
        (Bill required / согласие с условиями автоматического списания).
        """
        _open_yoomoney_form(driver)

        source = driver.page_source

        checkboxes = driver.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().className("android.widget.CheckBox")'
        )
        has_checkbox = len(checkboxes) > 0

        has_agreement_text = any(
            phrase in source
            for phrase in [
                "Bill required",
                "By making the payment",
                "Счёт обязателен",
                "автоматическ",
                "debiting money",
                "saving the card",
            ]
        )

        assert has_checkbox or has_agreement_text, (
            "Чекбокс согласия / блок условий не найден на форме оплаты YooMoney"
        )

    @allure.story("UI-08: Форма YooMoney содержит ссылки на документы")
    def test_yoomoney_form_shows_document_links(self, driver):
        """
        На форме оплаты YooMoney присутствуют ссылки на юридические документы
        («debiting money automatically» и «saving the card»).
        """
        _open_yoomoney_form(driver)

        source = driver.page_source

        assert "debiting money" in source or "saving the card" in source, (
            "Ссылки на документы (debiting money / saving the card) не найдены на форме YooMoney"
        )

        links = driver.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().clickable(true).descriptionContains("debiting")'
        ) + driver.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().clickable(true).descriptionContains("saving")'
        )
        assert len(links) > 0, (
            "Кликабельные ссылки на документы не найдены на форме YooMoney"
        )

    @allure.story("UI-09: Форма YooMoney содержит поля ввода платёжных данных")
    def test_yoomoney_form_shows_input_fields(self, driver):
        """
        На форме оплаты YooMoney присутствуют поля ввода карточных данных:
        номер карты, срок действия (MM/YY), CVC.
        Опционально — поле email для отправки чека.
        """
        _open_yoomoney_form(driver)

        source = driver.page_source

        fields = driver.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().className("android.widget.EditText")'
        )

        assert len(fields) >= 3 or "Card number" in source or 'hint="CVC"' in source, (
            f"Поля ввода карточных данных не найдены на форме YooMoney. "
            f"EditText-полей: {len(fields)}"
        )

        if len(fields) >= 3:
            hints = [f.get_attribute("hint") or "" for f in fields]
            assert any(h in ("MM", "YY", "CVC") for h in hints), (
                f"Поля MM/YY/CVC не найдены среди полей формы. Hints: {hints}"
            )
