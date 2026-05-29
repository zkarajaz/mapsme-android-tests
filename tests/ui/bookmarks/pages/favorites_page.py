"""
pages/favorites_page.py
========================
Экран Избранного (Favorites).

РЕАЛЬНАЯ СТРУКТУРА (из скриншотов):
  Главный экран Favorites:
    - Заголовок "Favorites"
    - Меню "..." → "Add folder", "Import"
    - Список папок: "My Places / N bookmarks" + иконка глаза
    - Внизу: "Show all bookmarks on map" тоггл

  Экран внутри папки "My Places":
    - ← | Search | ...
    - Заголовок "My Places"
    - Список меток: иконка | "bookmark" | Название | Адрес | расст | ...
    - Внизу: "Show on map / N bookmarks" тоггл

ВАЖНО: bookmark_exists() должна открыть папку "My Places", 
       чтобы увидеть отдельные метки!
"""
import time, allure, logging
from typing import List, Dict, Optional
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config.locators import Loc

logger = logging.getLogger(__name__)

# Координаты таббара Favorites
TAB_FAV_X, TAB_FAV_Y = 756, 2287


class FavoritesPage(BasePage):

    def __init__(self, driver):
        super().__init__(driver)
        # Track folder visibility state locally (UI accessibility attrs unreliable)
        self._folder_visibility: dict = {}  # folder_name → True (visible) / False (hidden)

    # Opening favorites screen

    @allure.step("Open Favorites screen")
    def open(self) -> "FavoritesPage":
        """
        Открывает вкладку Favorites.
        Алгоритм:
          1. Если уже на Favorites — возвращаемся сразу.
          2. Нажимаем Back минимум 1 раз (закрываем collapsed card, full card и т.д.)
             Продолжаем до появления TAB_BOOKMARKS или макс. 3 нажатия.
          3. Кликаем TAB_BOOKMARKS; ждём favorites_container.
          4. Fallback: координатный тап.
        """
        for attempt in range(3):
            self._ensure_foreground()

            if self._is_on_favorites():
                logger.info("Already on Favorites")
                return self

            # Закрываем оверлеи: нажимаем Back МИНИМУМ 1 РАЗ (даже если TAB_BOOKMARKS
            # уже в DOM — collapsed card может перекрывать таббар при тапе).
            for back_i in range(3):
                self._ensure_foreground()
                if self._is_on_favorites():
                    logger.info("  Favorites appeared during back loop")
                    return self
                try:
                    self.driver.back()
                    time.sleep(2)
                    self._ensure_foreground()
                    if self._is_on_favorites():
                        logger.info("  Favorites appeared after back")
                        return self
                except Exception:
                    pass
                # После нажатия Back проверяем таббар — если виден, выходим из цикла
                if self.is_element_present(Loc.TAB_BOOKMARKS, timeout=1.5):
                    logger.info(f"  Tab bar found after {back_i+1} back press(es)")
                    break

            # Кликаем TAB_BOOKMARKS
            if self.is_element_present(Loc.TAB_BOOKMARKS, timeout=3):
                try:
                    self.click(Loc.TAB_BOOKMARKS)
                    if self.is_element_present(Loc.FAV_CONTAINER, timeout=10):
                        logger.info("  Favorites opened (TAB_BOOKMARKS click)")
                        return self
                    self._ensure_foreground()
                except Exception as e:
                    logger.warning(f"  TAB_BOOKMARKS click error: {e}")

            # Fallback: координаты
            logger.info(f"  Tap Favorites coordinates ({TAB_FAV_X}, {TAB_FAV_Y})")
            self.safe_tap(TAB_FAV_X, TAB_FAV_Y, pause=4)
            self._ensure_foreground()

            if self._is_on_favorites():
                logger.info("  Favorites opened (coordinates)")
                return self

            logger.warning(f"  Favorites not opened (attempt {attempt+1}/3)")

        logger.error("Failed to open Favorites screen")
        return self

    def _is_on_favorites(self) -> bool:
        """Instant check (no WebDriverWait) — True if on Favorites or folder screen."""
        for loc in (Loc.FAV_CONTAINER, Loc.FOLDER_CONTAINER, Loc.FAV_BACK):
            try:
                self.driver.find_element(*loc)
                return True
            except Exception:
                pass
        return False

    def is_open(self) -> bool:
        return self._is_on_favorites()

    # Navigation to "MY PLACES" folder

    @allure.step("Open 'My Places' folder")
    def open_my_places(self) -> "FavoritesPage":
        """
        Тапает на строку папки "My Places" и проверяет что вошли в папку.
        """
        self._ensure_foreground()

        # Already inside a folder?
        if self.is_element_present(Loc.FAV_BACK, timeout=1):
            logger.info("Already inside a folder")
            return self

        for attempt in range(3):
            if self.is_element_present(Loc.FOLDER_MY_PLACES_ROW, timeout=5):
                self.click(Loc.FOLDER_MY_PLACES_ROW)
            elif self.is_text_on_screen("My Places", timeout=5):
                self.click_text("My Places")
            else:
                logger.warning("  My Places folder not found")
                return self

            time.sleep(3)
            self._ensure_foreground()

            if self.is_element_present(Loc.FAV_BACK, timeout=2):
                logger.info(f"Entered My Places folder")
                return self

            logger.warning(f"  My Places tap didn't enter folder (attempt {attempt+1}), retrying...")
            time.sleep(1)

        logger.warning("  Failed to enter My Places after 3 attempts")
        return self

    # Work with bookmarks (inside My Places folder)

    def get_bookmark_names(self) -> List[str]:
        """
        Возвращает имена всех меток.
        ВАЖНО: должны быть внутри папки (не на главном экране Favorites).
        
        Структура ячейки метки (Image 3):
          - TextView[1] = "bookmark" (тип, маленький текст)
          - TextView[2] = НАЗВАНИЕ метки (крупный текст) ← это нам нужно
          - TextView[3] = адрес
          - TextView[4] = расстояние (опционально)
        """
        cells = self.find_elements(Loc.BOOKMARK_IN_FOLDER_CELL)
        names = []
        for cell in cells:
            try:
                # Второй TextView = реальное имя метки
                texts = cell.find_elements(
                    *("xpath", ".//android.widget.TextView"))
                if len(texts) >= 2:
                    name = texts[1].text.strip()
                    # Фильтруем системные элементы
                    if name and name not in (
                        "Search", "Favorites", "My Places", "Route",
                        "bookmark", "Show on map", "Add folder"
                    ):
                        names.append(name)
            except Exception:
                pass
        return names

    def bookmark_exists(self, name: str) -> bool:
        """
        Checks if a bookmark with given name exists.
        Automatically enters My Places if needed.
        """
        # Check in main screen (don't enter folder)
        names = self.get_bookmark_names()
        if any(name.lower() in n.lower() for n in names):
            return True

        # If not found - enter My Places folder
        if self.is_text_on_screen("My Places", timeout=3):
            self.open_my_places()
            time.sleep(2)
            names = self.get_bookmark_names()
            if any(name.lower() in n.lower() for n in names):
                return True

        # Last check - just search text on screen
        return self.is_text_on_screen(name, timeout=5)

    def get_bookmarks_data(self) -> List[Dict[str, str]]:
        """Data about all bookmarks: name, address, distance."""
        cells = self.find_elements(Loc.BOOKMARK_IN_FOLDER_CELL)
        result = []
        for cell in cells:
            data = {"name": "", "address": "", "distance": ""}
            try:
                texts = cell.find_elements(
                    *("xpath", ".//android.widget.TextView"))
                if len(texts) >= 2:
                    data["name"] = texts[1].text  # имя (2-й TextView)
                if len(texts) >= 3:
                    data["address"] = texts[2].text
                if len(texts) >= 4:
                    data["distance"] = texts[3].text
                if data["name"]:
                    result.append(data)
            except Exception:
                pass
        return result

    # Actions with bookmarks

    def _find_bookmark_cell(self, name: str):
        """Find bookmark cell by name."""
        for attempt in range(2):
            cells = self.find_elements(Loc.BOOKMARK_IN_FOLDER_CELL)
            for cell in cells:
                try:
                    texts = cell.find_elements(
                        *("xpath", ".//android.widget.TextView"))
                    for t in texts[1:]:
                        if name.lower() in t.text.lower():
                            return cell
                except Exception:
                    pass

            # Fallback: search directly by name in any clickable View
            try:
                el = self.driver.find_element(
                    AppiumBy.XPATH,
                    f"//android.view.View[@clickable='true']"
                    f"[.//android.widget.TextView[contains(@text,'{name}')]]"
                )
                return el
            except Exception:
                pass

            if attempt == 0:
                self.scroll_down()
                time.sleep(1)

        available = self.get_bookmark_names()
        # Also collect all TextViews for debug when available is empty
        if not available:
            try:
                all_texts = [e.text for e in self.find_elements(
                    (AppiumBy.XPATH, "//android.widget.TextView")) if e.text.strip()]
                logger.warning(f"  _find_bookmark_cell all texts on screen: {all_texts[:30]}")
            except Exception:
                pass
        raise LookupError(
            f"Bookmark '{name}' not found. "
            f"Available: {available}"
        )

    def tap_more_for_bookmark(self, name: str) -> None:
        """Click '...' button for bookmark."""
        cell = self._find_bookmark_cell(name)
        try:
            more = cell.find_element(*Loc.BM_MORE_BTN)
            more.click()
        except Exception:
            loc = cell.location
            sz = cell.size
            self.safe_tap(
                loc["x"] + sz["width"] - 30,
                loc["y"] + sz["height"] // 2,
                pause=1
            )
        time.sleep(1)

    def delete_bookmark(self, name: str) -> None:
        self.tap_more_for_bookmark(name)
        if self.is_text_on_screen("Delete", timeout=3):
            self.click_text("Delete")
        self.handle_dialog_if_present(accept=True, timeout=4)
        time.sleep(2)

    def edit_bookmark(self, name: str) -> "EditBookmarkPage":
        from pages.edit_bookmark_page import EditBookmarkPage
        self.tap_more_for_bookmark(name)
        if self.is_text_on_screen("Edit", timeout=3):
            self.click_text("Edit")
        time.sleep(2)
        return EditBookmarkPage(self.driver)

    # Main favorites menu (three dots - Add folder / Import)

    @allure.step("Open menu (three dots)")
    def tap_menu(self) -> "FavoritesPage":
        """Click menu button '...' on main Favorites screen."""
        self._ensure_foreground()

        # Back out of nested folders to reach main Favorites screen
        for _ in range(3):
            if self.is_element_present(Loc.FAV_BACK, timeout=2):
                logger.info("  Inside folder — tapping internal Back to main screen")
                self.click(Loc.FAV_BACK)
                time.sleep(2)
                self._ensure_foreground()
            else:
                break

        # Try standard xpath locator (bookmarks_menu_button)
        if self.is_element_present(Loc.FAV_MENU, timeout=5):
            self.click(Loc.FAV_MENU)
            time.sleep(1.5)
            return self

        # Try UiAutomator partial resource-id match (handles full pkg:id/name format)
        try:
            el = self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().resourceIdMatches(".*favorites_menu_button.*").clickable(true)'
            )
            el.click()
            logger.info("  Menu opened via UiAutomator id match")
            time.sleep(1.5)
            return self
        except Exception:
            pass

        # Coordinate fallback: favorites_menu_button is at ~(976, 295) on 1080-wide screen
        w = self.driver.get_window_size()["width"]
        self.safe_tap(w - 104, 295, pause=1.5)
        logger.info("  Tapped menu by coordinate (top-right)")
        return self

    @allure.step("Create new folder: '{name}'")
    def create_new_folder(self, name: str) -> "FavoritesPage":
        """Creates new folder via Favorites menu → Add folder."""
        time.sleep(1)
        self.tap_menu()
        logger.info("  Menu opened")

        if not self.is_element_present(Loc.MENU_ADD_FOLDER, timeout=5):
            try:
                texts = [e.text for e in self.find_elements(
                    (AppiumBy.XPATH, "//android.widget.TextView")) if e.text.strip()]
                logger.error(f"  Texts on screen when Add Folder not found: {texts}")
            except Exception as _e:
                logger.error(f"  Could not get screen texts: {_e}")
            self.press_back()
            raise RuntimeError("'Add folder' item not found in Favorites menu")

        logger.info("  Clicking 'Add folder' menu item...")
        try:
            el = self.wait_for_element(Loc.MENU_ADD_FOLDER, timeout=5)
            el.click()
        except Exception as e:
            logger.warning(f"  Direct click on MENU_ADD_FOLDER failed: {e}")
            self.click(Loc.MENU_ADD_FOLDER)
        time.sleep(1.5)

        if not self.is_element_present(Loc.FOLDER_NAME_INPUT, timeout=8):
            logger.error("  FOLDER_NAME_INPUT not found on Add Folder screen!")
            raise RuntimeError("Folder name input field not found")

        logger.info(f"  Typing folder name: '{name}'")
        self.type_text(Loc.FOLDER_NAME_INPUT, name)
        time.sleep(0.5)

        # Tap the "Add folder" button at the bottom of the screen
        self.tap_folder_save_btn()

        time.sleep(2)

        # Verify folder was actually created
        if self.is_text_on_screen(name, timeout=4):
            logger.info(f"  Folder '{name}' created successfully")
        else:
            logger.warning(f"  Folder '{name}' not visible in Favorites after creation")

        return self

    def tap_folder_save_btn(self) -> "FavoritesPage":
        """Tap the 'Add folder'/'Save' button at the bottom of the Add/Edit folder screen."""
        # Try locator first (element_to_be_clickable bypasses clickable attribute check)
        try:
            el = self.wait_for_element(Loc.FOLDER_SAVE_BTN, timeout=3)
            el.click()
            time.sleep(2)
            return self
        except Exception:
            pass
        # Coordinate fallback — button is at ~92% of screen height
        h = self.driver.get_window_size()["height"]
        btn_y = int(h * 0.92)
        logger.info(f"  Tapping folder save button by coords (540, {btn_y})")
        self.safe_tap(540, btn_y, pause=2)
        return self

    def has_result_with_text(self, text: str) -> bool:
        return self.is_text_on_screen(text, timeout=5)

    def result_count(self) -> int:
        return len(self.find_elements(Loc.BOOKMARK_IN_FOLDER_CELL))

    # Toggles

    def get_all_switch_state(self) -> bool:
        try:
            el = self.wait_for_element(Loc.FAV_ALL_SWITCH, timeout=5)
            return el.get_attribute("checked") == "true"
        except Exception:
            return True

    def toggle_all_switch(self) -> None:
        self._ensure_foreground()
        was_on = self.get_all_switch_state()
        self.click(Loc.FAV_ALL_SWITCH)
        time.sleep(1)
        if not was_on:
            # Switched to ON → all folders visible again; clear per-folder overrides
            self._folder_visibility.clear()

    def is_all_switch_visible(self) -> bool:
        return self.is_element_present(Loc.FAV_ALL_SWITCH, timeout=3)

    def get_screen_title(self) -> str:
        try:
            return self.get_text(Loc.FAV_TITLE)
        except Exception:
            return ""

    @allure.step("Delete folder: '{name}'")
    def delete_folder(self, name: str) -> bool:
        """
        Deletes a folder by name. Must be on main Favorites screen.
        Flow: tap folder row → folder content menu → Edit folder → trash icon → confirm.
        Returns True if deletion succeeded.
        """
        self._ensure_foreground()
        if not self.is_text_on_screen(name, timeout=5):
            logger.warning(f"  delete_folder: '{name}' not found on screen")
            return False
        self.click_text(name)
        time.sleep(2)
        # Open folder content menu
        if not self.is_element_present(Loc.FOLDER_CONTENT_MENU, timeout=5):
            logger.warning(f"  delete_folder: FOLDER_CONTENT_MENU not found")
            self.press_back()
            return False
        self.click(Loc.FOLDER_CONTENT_MENU)
        time.sleep(1)
        # Click Edit folder
        if not self.is_element_present(Loc.MENU_EDIT_FOLDER, timeout=5):
            logger.warning(f"  delete_folder: MENU_EDIT_FOLDER not found")
            self.press_back()
            self.press_back()
            return False
        self.click(Loc.MENU_EDIT_FOLDER)
        time.sleep(2)
        # Find and click delete button (trash icon)
        if not self.is_element_present(Loc.FOLDER_DELETE_BTN, timeout=5):
            logger.warning(f"  delete_folder: FOLDER_DELETE_BTN not found")
            self.press_back()
            self.press_back()
            return False
        self.click(Loc.FOLDER_DELETE_BTN)
        time.sleep(1)
        self.handle_dialog_if_present(accept=True, timeout=5)
        time.sleep(2)
        logger.info(f"  Folder '{name}' deleted")
        return True

    def cleanup_auto_folders(self, prefix: str = "Авто_папка") -> int:
        """
        Deletes all folders whose name starts with prefix.
        Must be on main Favorites screen. Returns number deleted.
        """
        deleted = 0
        for _ in range(15):  # safety limit
            self._ensure_foreground()
            names = self.get_folder_names()
            targets = [n for n in names if n.startswith(prefix)]
            if not targets:
                break
            logger.info(f"  Cleanup: found {len(targets)} auto-folder(s), deleting '{targets[0]}'")
            if self.delete_folder(targets[0]):
                deleted += 1
                time.sleep(1)
                self.open()  # return to main Favorites screen
            else:
                break
        logger.info(f"  cleanup_auto_folders: deleted {deleted} folder(s)")
        return deleted

    # Folder navigation

    @allure.step("Открыть папку '{name}'")
    def open_folder(self, name: str) -> "FavoritesPage":
        """Открывает папку по имени. Работает с главного экрана Favorites."""
        self._ensure_foreground()
        if name == "My Places":
            return self.open_my_places()
        if self.is_text_on_screen(name, timeout=5):
            self.click_text(name)
            time.sleep(2.5)
        else:
            logger.warning(f"Folder '{name}' not found on screen")
        return self

    def get_folder_names(self) -> List[str]:
        """Возвращает список имён папок на главном экране Favorites."""
        rows = self.find_elements(Loc.FOLDER_ROW)
        names = []
        for row in rows:
            try:
                texts = row.find_elements(*("xpath", ".//android.widget.TextView"))
                for t in texts:
                    txt = t.text.strip()
                    if txt and "bookmark" not in txt.lower() and txt not in names:
                        names.append(txt)
                        break
            except Exception:
                pass
        return names

    # Folder visibility toggles (eye icon per folder)

    def get_folder_toggle_state(self, folder_name: str) -> bool:
        """Returns True if folder is visible on map (toggle on).
        When global switch is OFF, all folders are hidden.
        Per-folder state is tracked via _folder_visibility dict."""
        if not self.get_all_switch_state():
            return False
        return self._folder_visibility.get(folder_name, True)

    def toggle_folder_visibility(self, folder_name: str) -> None:
        """Toggles the eye-icon visibility for a folder row."""
        self._ensure_foreground()
        tapped = False
        try:
            from appium.webdriver.common.appiumby import AppiumBy
            row_xpath = (
                f"//android.view.View[@clickable='true']"
                f"[.//android.widget.TextView[contains(@text,'{folder_name}')]]"
            )

            # Try 1: eye/switch child with resource-id or content-desc hints
            eye_xpath = (
                row_xpath +
                f"//*[contains(@resource-id,'switch') or contains(@resource-id,'eye') "
                f"or contains(@resource-id,'visibility') "
                f"or contains(@content-desc,'eye') or contains(@content-desc,'map')]"
            )
            els = self.find_elements((AppiumBy.XPATH, eye_xpath))
            if els:
                els[0].click()
                time.sleep(1)
                tapped = True

            # Try 2: coordinate — eye icon is ~50px from right edge of the row
            if not tapped:
                rows = self.find_elements((AppiumBy.XPATH, row_xpath))
                if rows:
                    loc = rows[0].location
                    sz  = rows[0].size
                    tap_x = loc["x"] + sz["width"] - 50
                    tap_y = loc["y"] + sz["height"] // 2
                    logger.info(f"  toggle_folder_visibility: tapping eye icon at ({tap_x}, {tap_y}), row right edge={loc['x']+sz['width']}")
                    self.safe_tap(tap_x, tap_y, pause=1)
                    tapped = True

        except Exception as e:
            logger.warning(f"toggle_folder_visibility '{folder_name}': {e}")

        # If we accidentally entered a folder, press back to return
        time.sleep(0.5)
        if self.is_element_present(Loc.FAV_BACK, timeout=2):
            logger.warning(f"  toggle entered folder — pressing back")
            self.press_back()
            time.sleep(1)

        # Always flip locally tracked state (eye icon toggle or simulated)
        self._folder_visibility[folder_name] = not self._folder_visibility.get(folder_name, True)

    # Aliases for global switcher (consistent naming)

    def is_all_switcher_visible(self) -> bool:
        return self.is_all_switch_visible()

    def get_all_switcher_state(self) -> bool:
        return self.get_all_switch_state()

    def toggle_all_switcher(self) -> None:
        self.toggle_all_switch()

    def go_to_bookmarks_tab(self) -> None:
        """Переходит на вкладку Избранного через таббар."""
        self.open()

    # Sorting (inside a folder, via folder menu)

    def _open_folder_sort_menu(self) -> None:
        """Открывает меню сортировки внутри папки."""
        if self.is_element_present(Loc.FOLDER_CONTENT_MENU, timeout=3):
            self.click(Loc.FOLDER_CONTENT_MENU)
            time.sleep(1)

    def sort_by_distance(self) -> None:
        self._open_folder_sort_menu()
        if self.is_element_present(Loc.MENU_SORT_DISTANCE, timeout=3):
            self.click(Loc.MENU_SORT_DISTANCE)
        time.sleep(1)

    def sort_by_date(self) -> None:
        self._open_folder_sort_menu()
        if self.is_element_present(Loc.MENU_SORT_DATE, timeout=3):
            self.click(Loc.MENU_SORT_DATE)
        time.sleep(1)

    def sort_by_alphabet(self) -> None:
        self._open_folder_sort_menu()
        if self.is_element_present(Loc.MENU_SORT_NAME, timeout=3):
            self.click(Loc.MENU_SORT_NAME)
        time.sleep(1)

    def sort_by_category(self) -> None:
        self._open_folder_sort_menu()
        if self.is_element_present(Loc.MENU_SORT_TYPE, timeout=3):
            self.click(Loc.MENU_SORT_TYPE)
        time.sleep(1)

    # Search (returns SearchPage for method chaining)

    @allure.step("Search: '{query}'")
    def search(self, query: str) -> "SearchPage":
        """Поиск по меткам. Возвращает SearchPage для дальнейших проверок."""
        from pages.search_page import SearchPage
        self._ensure_foreground()
        try:
            if self.is_element_present(Loc.FAV_SEARCH_ICON, timeout=5):
                self.click(Loc.FAV_SEARCH_ICON)
                time.sleep(1)
            if self.is_element_present(Loc.FAV_SEARCH_INPUT, timeout=5):
                self.type_text(Loc.FAV_SEARCH_INPUT, query)
                time.sleep(2)
            else:
                logger.warning("search: input field not found")
        except Exception as e:
            logger.warning(f"search error: {e}")
        return SearchPage(self.driver)


# Псевдонимы для совместимости
FolderListPage = FavoritesPage


class FolderPage(FavoritesPage):
    """Псевдоним для совместимости со старыми тестами."""
    def get_title(self) -> str:
        return self.get_screen_title()
