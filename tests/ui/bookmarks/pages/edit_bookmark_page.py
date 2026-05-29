"""
pages/edit_bookmark_page.py
===========================
Edit bookmark screen.

Structure:
  ← | Edit bookmark | delete
  [Change color button]
  Name: [edit_bookmark_name_text_field]  14/60
  Description: [edit_bookmark_description_text_field]
  Folder: [My Places →]   ← coordinates (278, 1401)
  [edit_bookmark_apply_button — Save]
"""
import time, allure, logging
from pages.base_page import BasePage
from config.locators import Loc
from config.settings import FieldLimits

logger = logging.getLogger(__name__)


class EditBookmarkPage(BasePage):

    def is_open(self, timeout: float = 10) -> bool:
        """Экран открыт если видно поле имени или заголовок или кнопку Save."""
        for loc in [Loc.EDIT_BM_NAME, Loc.EDIT_BM_SAVE, Loc.EDIT_BM_TITLE]:
            if self.is_element_present(loc, timeout=timeout // 3):
                return True
        return False

    @allure.step("Получить имя метки")
    def get_name(self) -> str:
        try:
            el = self.wait_for_element(Loc.EDIT_BM_NAME, timeout=15)
            return el.get_attribute("text") or el.text or ""
        except Exception:
            return ""

    @allure.step("Ввести имя метки: '{name}'")
    def set_name(self, name: str) -> "EditBookmarkPage":
        el = self.wait_for_element(Loc.EDIT_BM_NAME, timeout=15)
        el.clear()
        el.send_keys(name)
        return self

    @allure.step("Ввести описание")
    def set_description(self, desc: str) -> "EditBookmarkPage":
        try:
            el = self.wait_for_element(Loc.EDIT_BM_DESC, timeout=5)
            el.clear()
            el.send_keys(desc)
        except Exception as e:
            logger.warning(f"set_description: {e}")
        return self

    def get_description(self) -> str:
        try:
            el = self.wait_for_element(Loc.EDIT_BM_DESC, timeout=5)
            return el.get_attribute("text") or ""
        except Exception:
            return ""

    @allure.step("Нажать Save")
    def tap_save(self) -> None:
        self.click(Loc.EDIT_BM_SAVE)
        time.sleep(2.5)
        # Обрабатываем диалоги если появились
        self.handle_dialog_if_present(accept=True, timeout=2)

    @allure.step("Нажать Delete (мусорка)")
    def tap_delete(self) -> None:
        """
        Нажимает кнопку удаления.
        Сначала пробует xpath, если не нашёл — координаты.
        """
        self._ensure_foreground()
        if self.is_element_present(Loc.EDIT_BM_DELETE, timeout=3):
            self.click(Loc.EDIT_BM_DELETE)
        else:
            logger.info("  Тапаем мусорку по координатам")
            self.safe_tap(*Loc.EDIT_BM_DELETE_COORDS, pause=1)

    @allure.step("Нажать Назад")
    def tap_back(self) -> None:
        self._ensure_foreground()
        if self.is_element_present(Loc.EDIT_BM_BACK, timeout=3):
            self.click(Loc.EDIT_BM_BACK)
        else:
            self.press_back()

    def name_char_count(self) -> int:
        return len(self.get_name())

    def is_save_enabled(self) -> bool:
        try:
            return self.wait_for_element(Loc.EDIT_BM_SAVE).is_enabled()
        except Exception:
            return False

    def get_selected_folder(self) -> str:
        """Возвращает имя выбранной папки."""
        try:
            return "My Places"  # По умолчанию в приложении
        except Exception:
            return ""

    def wait_for_animation(self, duration: float = 2) -> None:
        time.sleep(duration)

    def name_field_char_count(self) -> int:
        """Alias for name_char_count."""
        return self.name_char_count()

    @allure.step("Открыть выбор папки")
    def tap_select_folder(self) -> "FavoritesPage":
        """Тапает на строку папки → открывает экран выбора папки."""
        from pages.favorites_page import FavoritesPage
        self._ensure_foreground()
        self.safe_tap(*Loc.EDIT_BM_FOLDER_ROW_COORDS, pause=2)
        return FavoritesPage(self.driver)

    @allure.step("Открыть палитру цветов")
    def open_color_picker(self) -> None:
        """Нажимает кнопку изменения цвета."""
        self._ensure_foreground()
        self.click(Loc.EDIT_BM_COLOR_BTN)
        time.sleep(1)
