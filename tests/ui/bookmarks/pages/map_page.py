"""
pages/map_page.py
=================
Карта MAPS.ME.

ФЛОУ ДОБАВЛЕНИЯ МЕТКИ:
  1. ensure_on_map() → закрыть всё лишнее, убедиться что мы на карте
  2. open_any_object() → тап по карте → свёрнутая карточка появляется
  3. _expand_card() → свайп вверх → полная карточка
  4. tap_bookmark_btn() → добавить в избранное (place_bookmark_button)
  5. open_edit_bookmark() → нажать карандаш у "My Places"

ПЕРЕХОД В ТАББАР:
  Вместо тапа по координатам таббара — используем элемент xpath.
  Если элемент не найден (приложение свернулось) — восстанавливаем и повторяем.
"""
import time, allure, logging, subprocess
from pages.base_page import BasePage
from config.locators import Loc

logger = logging.getLogger(__name__)

PKG = "com.mapswithme.maps.pro"
ADB = r"C:\Users\Victoria\AppData\Local\Android\Sdk\platform-tools\adb.exe"


class MapPage(BasePage):

    def ensure_on_map(self, close_panels: int = 2) -> None:
        """
        Убеждается что MAPS.ME активен и мы на экране карты.
        Закрывает открытые панели/карточки нажатием Назад.
        """
        # Сначала убеждаемся что приложение на переднем плане
        if not self._ensure_foreground(max_attempts=3):
            # Запускаем через ADB как крайняя мера
            try:
                subprocess.run(
                    [ADB, "-s", "emulator-5554", "shell", "am", "start", "-n",
                     f"{PKG}/com.mapswithme.maps.pro.DefaultIcon"],
                    timeout=10, capture_output=True
                )
                time.sleep(5)
            except Exception as e:
                logger.warning(f"ADB start failed: {e}")

        # Закрываем открытые панели
        for _ in range(close_panels):
            try:
                self.driver.back()
                time.sleep(1.5)
                self._ensure_foreground()
            except Exception:
                break

        # Закрываем диалоги если есть
        self.handle_dialog_if_present(accept=False, timeout=2)
        time.sleep(1)

    @allure.step("Открыть карточку объекта на карте")
    def open_any_object(self) -> "ObjectCardPage":
        """
        Открывает карточку объекта:
          1. Тапаем по карте (несколько позиций)
          2. Ищем place_bookmark_button (свёрнутая карточка)
          3. Свайп вверх → полная карточка

        Жёсткий таймаут 35 секунд, потом возвращаем как есть.
        """
        from pages.object_card_page import ObjectCardPage

        # Позиции для тапа на карте (верхняя часть, подальше от таббара)
        # y=0.15-0.65 — безопасная зона, таббар начинается ~y=0.91
        tap_positions = [
            (0.50, 0.15),   # верхний центр
            (0.50, 0.30),   # центр-верх
            (0.50, 0.45),   # центр
            (0.30, 0.25),   # левее
            (0.70, 0.35),   # правее
            (0.50, 0.60),   # центр-низ
            (0.35, 0.50),   # диагональ
        ]

        card = ObjectCardPage(self.driver)
        deadline = time.time() + 35

        for x_pct, y_pct in tap_positions:
            if time.time() > deadline:
                logger.error("Timeout 35s when opening card")
                break

            logger.info(f"Tap on map ({x_pct:.2f}, {y_pct:.2f})")

            # Safe tap (includes collapse check)
            self.safe_tap_pct(x_pct, y_pct, pause=0)

            # Wait for flag to appear (max 8s)
            wait_until = time.time() + 8
            while time.time() < wait_until:
                # If app collapsed - recover and break waiting
                if not self._ensure_foreground():
                    break
                if self.is_element_present(Loc.CARD_BOOKMARK_BTN, timeout=2):
                    logger.info("Card appeared (flag found)")
                    self._expand_card()
                    return card
                time.sleep(0.5)

            # Card did not appear - close and try another position
            logger.info("  Card did not appear, trying next position...")
            self._ensure_foreground()
            try:
                self.driver.back()
                time.sleep(1)
                self._ensure_foreground()
            except Exception:
                pass

        logger.warning("Card not found")
        return card

    def _expand_card(self) -> None:
        """
        Swipe up to expand card.
        Gray bar is at about 82% of screen height.
        """
        self._ensure_foreground()
        size = self.driver.get_window_size()
        w, h = size["width"], size["height"]
        sy = int(h * 0.82)
        ey = int(h * 0.30)
        logger.info(f"Swipe up: ({w//2},{sy}) → ({w//2},{ey})")
        self.swipe(w // 2, sy, w // 2, ey, 600)
        time.sleep(2.5)

    @allure.step("Перейти на вкладку Favorites")
    def go_to_favorites(self) -> "FavoritesPage":
        """
        Переходит на вкладку Favorites через xpath-элемент.
        Если элемент не найден (приложение свернулось) — восстанавливает.
        """
        from pages.favorites_page import FavoritesPage
        return _navigate_to_tab(self.driver, "favorites")

    @allure.step("Перейти на вкладку Search")
    def go_to_search(self) -> None:
        _navigate_to_tab(self.driver, "search")

    @allure.step("Поиск '{query}' на карте → открыть карточку объекта")
    def search_and_open(self, query: str) -> "ObjectCardPage":
        """
        Открывает объект через поиск на карте.
          1. Нажимает вкладку Search.
          2. Вводит запрос.
          3. Тапает по первому результату.
          4. Раскрывает карточку и возвращает ObjectCardPage.
        """
        from pages.object_card_page import ObjectCardPage
        from appium.webdriver.common.appiumby import AppiumBy

        self._ensure_foreground()

        # Закрываем любую открытую карточку чтобы освободить таббар
        try:
            self.driver.back()
            time.sleep(1.5)
            self._ensure_foreground()
        except Exception:
            pass

        # Открываем вкладку поиска
        if self.is_element_present(Loc.TAB_SEARCH, timeout=5):
            self.click(Loc.TAB_SEARCH)
            time.sleep(2)
        else:
            logger.warning("search_and_open: вкладка поиска не найдена")

        # Вводим запрос
        search_input = (AppiumBy.XPATH, "//android.widget.EditText[1]")
        if self.is_element_present(search_input, timeout=8):
            self.type_text(search_input, query)
            time.sleep(2.5)
        else:
            logger.warning("search_and_open: поле ввода поиска не найдено")

        # Тапаем по первому результату содержащему запрос
        result_loc = (AppiumBy.XPATH,
            f"//*[contains(@text,'{query}')][@clickable='true']"
            f" | //*[contains(@content-desc,'{query}')][@clickable='true']")
        if self.is_element_present(result_loc, timeout=5):
            self.click(result_loc)
            time.sleep(2)
        else:
            # Fallback: первый кликабельный View в списке результатов
            fallback = (AppiumBy.XPATH,
                "//android.widget.ListView//android.view.View[@clickable='true'][1]"
                " | //android.widget.RecyclerView//android.view.View[@clickable='true'][1]")
            if self.is_element_present(fallback, timeout=3):
                self.click(fallback)
                time.sleep(2)
            else:
                logger.warning(f"search_and_open: результат '{query}' не найден")

        # Раскрываем карточку если нужно
        if self.is_element_present(Loc.CARD_BOOKMARK_BTN, timeout=4):
            self._expand_card()

        return ObjectCardPage(self.driver)

    def is_bookmark_marker_visible(self, timeout: float = 3) -> bool:
        """Проверяет наличие маркера метки на карте."""
        from appium.webdriver.common.appiumby import AppiumBy
        marker_loc = (AppiumBy.XPATH,
            "//*[contains(@resource-id,'bookmark') "
            "and (contains(@resource-id,'pin') or contains(@resource-id,'marker'))]"
            " | //*[@content-desc='bookmark pin']")
        return self.is_element_present(marker_loc, timeout=timeout)


def _navigate_to_tab(driver, tab_name: str, max_attempts: int = 3):
    """
    Универсальный переход на вкладку таббара с retry при сворачивании.
    tab_name: 'favorites', 'search', 'hub', 'routes', 'more'
    """
    from pages.favorites_page import FavoritesPage
    from pages.base_page import BasePage

    tab_map = {
        "favorites": (Loc.TAB_BOOKMARKS, Loc.TAB_BOOKMARKS_COORDS),
        "search":    (Loc.TAB_SEARCH,    Loc.TAB_SEARCH_COORDS),
        "hub":       (Loc.TAB_HUB,       Loc.TAB_HUB_COORDS),
    }
    tab_loc, tab_coords = tab_map.get(tab_name,
                                       (Loc.TAB_BOOKMARKS, Loc.TAB_BOOKMARKS_COORDS))

    base = BasePage(driver)

    for attempt in range(max_attempts):
        # Восстанавливаем приложение
        base._ensure_foreground()
        time.sleep(1)

        # Пробуем найти элемент таббара через xpath
        if base.is_element_present(tab_loc, timeout=5):
            try:
                base.click(tab_loc)
                time.sleep(3)
                base._ensure_foreground()
                logger.info(f"Navigated to tab '{tab_name}' via xpath")
                break
            except Exception as e:
                logger.warning(f"  Click on tabbar (xpath) failed: {e}")

        # Fallback: tap by coordinates
        logger.info(f"  Tap coordinates {tab_coords} (attempt {attempt+1})")
        # First press back to close card
        try:
            driver.back()
            time.sleep(1.5)
            base._ensure_foreground()
        except Exception:
            pass

        base.safe_tap(*tab_coords, pause=3)
        base._ensure_foreground()

    if tab_name == "favorites":
        return FavoritesPage(driver)
    return None
