"""
pages/base_page.py
==================
Базовый Page Object. 

ГЛАВНАЯ ЗАЩИТА: Каждый tap_coords/tap_pct/click перед действием проверяет
что MAPS.ME на переднем плане. Если нет — восстанавливает и повторяет.
"""
import logging, time, allure
from typing import Tuple, Optional, List
from appium.webdriver.webdriver import WebDriver
from appium.webdriver.webelement import WebElement
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException,
    StaleElementReferenceException, WebDriverException
)
from config.settings import Timeouts

logger = logging.getLogger(__name__)

PKG = "com.mapswithme.maps.pro"
# Состояние приложения: 4 = на переднем плане (RUNNING_IN_FOREGROUND)
APP_STATE_FOREGROUND = 4


class BasePage:
    def __init__(self, driver: WebDriver):
        self.driver = driver

    # Protection against collapsing (applied everywhere automatically)

    def _ensure_foreground(self, max_attempts: int = 3) -> bool:
        """
        Проверяет что MAPS.ME на переднем плане.
        Если нет — восстанавливает. Возвращает True если успешно.
        """
        for attempt in range(max_attempts):
            try:
                state = self.driver.query_app_state(PKG)
                if state == APP_STATE_FOREGROUND:
                    return True
                logger.warning(
                    f"MAPS.ME minimized (state={state}), "
                    f"recovering... (attempt {attempt+1}/{max_attempts})"
                )
                self.driver.activate_app(PKG)
                time.sleep(3)
            except Exception as e:
                logger.warning(f"ensure_foreground error: {e}")
                try:
                    self.driver.activate_app(PKG)
                    time.sleep(3)
                except Exception:
                    pass
        return False

    def safe_tap(self, x: int, y: int, pause: float = 1.5,
                 retries: int = 2) -> bool:
        """
        Безопасный тап по координатам. Перед каждым тапом проверяет
        что приложение активно. Если сворачивается — повторяет.
        """
        for attempt in range(retries + 1):
            self._ensure_foreground()
            try:
                self.driver.tap([(x, y)])
                logger.debug(f"Tap ({x}, {y})")
                if pause > 0:
                    time.sleep(pause)
                return True
            except Exception as e:
                logger.warning(f"safe_tap ({x},{y}) попытка {attempt+1}: {e}")
                if attempt < retries:
                    self._ensure_foreground()
                    time.sleep(1)
        return False

    def safe_tap_pct(self, x_pct: float, y_pct: float,
                     pause: float = 1.5, retries: int = 2) -> bool:
        """Безопасный тап по проценту экрана."""
        size = self.driver.get_window_size()
        x = int(size["width"] * x_pct)
        y = int(size["height"] * y_pct)
        return self.safe_tap(x, y, pause=pause, retries=retries)

    # Алиасы для обратной совместимости
    def tap_coords(self, x: int, y: int, pause: float = 1.5) -> None:
        self.safe_tap(x, y, pause=pause)

    def tap_pct(self, x_pct: float, y_pct: float, pause: float = 1.5) -> None:
        self.safe_tap_pct(x_pct, y_pct, pause=pause)

    # Waiting

    def _wait(self, timeout: float) -> WebDriverWait:
        return WebDriverWait(
            self.driver, timeout,
            ignored_exceptions=[StaleElementReferenceException]
        )

    def wait_for_element(self, loc: Tuple,
                         timeout: float = Timeouts.EXPLICIT) -> WebElement:
        try:
            return self._wait(timeout).until(
                EC.presence_of_element_located(loc))
        except TimeoutException:
            self.take_screenshot("timeout")
            raise TimeoutException(
                f"Не найден ({timeout}с): {str(loc[1])[:60]}")

    def wait_for_visible(self, loc: Tuple,
                         timeout: float = Timeouts.EXPLICIT) -> WebElement:
        try:
            return self._wait(timeout).until(
                EC.visibility_of_element_located(loc))
        except TimeoutException:
            self.take_screenshot("not_visible")
            raise TimeoutException(
                f"Невидим ({timeout}с): {str(loc[1])[:60]}")

    def wait_for_invisible(self, loc: Tuple,
                           timeout: float = Timeouts.EXPLICIT) -> bool:
        try:
            return self._wait(timeout).until(
                EC.invisibility_of_element_located(loc))
        except TimeoutException:
            return False

    def wait_clickable(self, loc: Tuple,
                       timeout: float = Timeouts.EXPLICIT) -> WebElement:
        try:
            return self._wait(timeout).until(
                EC.element_to_be_clickable(loc))
        except TimeoutException:
            self.take_screenshot("not_clickable")
            raise TimeoutException(
                f"Не кликабелен ({timeout}с): {str(loc[1])[:60]}")

    def find_elements(self, loc: Tuple) -> List[WebElement]:
        try:
            return self.driver.find_elements(*loc)
        except Exception:
            return []

    def is_element_present(self, loc: Tuple, timeout: float = 5) -> bool:
        try:
            self._wait(timeout).until(EC.presence_of_element_located(loc))
            return True
        except (TimeoutException, NoSuchElementException, WebDriverException):
            return False

    # Actions

    def click(self, loc: Tuple, timeout: float = Timeouts.EXPLICIT) -> None:
        """Клик по элементу с защитой от сворачивания."""
        self._ensure_foreground()
        self.wait_clickable(loc, timeout).click()

    def type_text(self, loc: Tuple, text: str, clear: bool = True) -> None:
        el = self.wait_for_visible(loc)
        if clear:
            el.clear()
        el.send_keys(text)

    def get_text(self, loc: Tuple) -> str:
        return self.wait_for_visible(loc).text

    def swipe(self, sx: int, sy: int, ex: int, ey: int,
              dur: int = 800) -> None:
        self._ensure_foreground()
        self.driver.swipe(sx, sy, ex, ey, dur)

    def scroll_down(self, times: int = 1) -> None:
        sz = self.driver.get_window_size()
        for _ in range(times):
            self.swipe(
                sz["width"] // 2, int(sz["height"] * 0.7),
                sz["width"] // 2, int(sz["height"] * 0.3))
            time.sleep(0.5)

    def press_back(self) -> None:
        self._ensure_foreground()
        self.driver.back()
        time.sleep(1.5)

    # Dialogs

    def handle_dialog_if_present(self, accept: bool = True,
                                  timeout: float = 3) -> bool:
        """Обрабатывает диалог подтверждения если он появился."""
        from config.locators import Loc
        loc = Loc.DIALOG_OK if accept else Loc.DIALOG_CANCEL
        if self.is_element_present(loc, timeout=timeout):
            try:
                self.click(loc)
                time.sleep(1)
                logger.info(f"Диалог обработан (accept={accept})")
                return True
            except Exception:
                pass
        return False

    # Snacks

    def wait_for_success_snack(self,
                                timeout: float = Timeouts.SNACK_DISAPPEAR
                                ) -> bool:
        from config.locators import Loc
        return self.is_element_present(Loc.SNACK_SUCCESS, timeout=timeout)

    def wait_for_error_snack(self,
                              timeout: float = Timeouts.SNACK_DISAPPEAR
                              ) -> bool:
        from config.locators import Loc
        return self.is_element_present(Loc.SNACK_ERROR, timeout=timeout)

    # Screenshots and other

    def take_screenshot(self, name: str = "screenshot") -> bytes:
        try:
            png = self.driver.get_screenshot_as_png()
            allure.attach(png, name=name,
                          attachment_type=allure.attachment_type.PNG)
            return png
        except Exception:
            return b""

    def wait_anim(self, sec: float = Timeouts.ANIMATION) -> None:
        time.sleep(sec)

    def click_text(self, text: str, timeout: float = 10) -> None:
        loc = (AppiumBy.XPATH,
               f"//*[contains(@text,'{text}') "
               f"or contains(@content-desc,'{text}')]")
        self._ensure_foreground()
        self.wait_clickable(loc, timeout).click()

    def is_text_on_screen(self, text: str, timeout: float = 8) -> bool:
        loc = (AppiumBy.XPATH,
               f"//*[contains(@text,'{text}') "
               f"or contains(@content-desc,'{text}')]")
        return self.is_element_present(loc, timeout=timeout)
