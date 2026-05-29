"""
pages/object_card_page.py
=========================
Карточка объекта (bottom sheet).

ВАЖНО:
  - place_bookmark_button есть ТОЛЬКО в свёрнутой карточке (нижняя полоска)
  - После свайпа вверх (полная карточка) он снова появляется
  - "My Places" + карандаш появляются ТОЛЬКО после добавления метки
"""
import time, allure, logging
from pages.base_page import BasePage
from config.locators import Loc

logger = logging.getLogger(__name__)


class ObjectCardPage(BasePage):

    def is_card_open(self) -> bool:
        """Карточка открыта если виден флажок ИЛИ "My Places"."""
        return (
            self.is_element_present(Loc.CARD_BOOKMARK_BTN, timeout=5) or
            self.is_text_on_screen("My Places", timeout=3)
        )

    def is_bookmarked(self) -> bool:
        """Объект в избранном если видна строка 'My Places'."""
        return self.is_text_on_screen("My Places", timeout=4)

    @allure.step("Нажать кнопку флажка (добавить/убрать метку)")
    def tap_bookmark_btn(self) -> None:
        """
        Нажимает place_bookmark_button.
        Пробует xpath, если не найден — координаты.
        """
        self._ensure_foreground()

        if self.is_element_present(Loc.CARD_BOOKMARK_BTN, timeout=5):
            self.click(Loc.CARD_BOOKMARK_BTN)
        else:
            logger.warning("  place_bookmark_button не найден, тапаем по координатам")
            self.safe_tap(*Loc.CARD_BOOKMARK_COORDS, pause=0)

        time.sleep(2.5)

    @allure.step("Удалить метку (с подтверждением)")
    def remove_bookmark_with_confirmation(self) -> None:
        """Убирает метку и подтверждает диалог если нужно."""
        self.tap_bookmark_btn()
        self.handle_dialog_if_present(accept=True, timeout=4)
        time.sleep(2)

    @allure.step("Открыть экран Edit bookmark")
    def open_edit_bookmark(self) -> "EditBookmarkPage":
        """
        Открывает Edit bookmark.
        Порядок попыток:
          1. Если экран уже открыт — возвращаем как есть
          2. Нажимаем карандаш рядом с "My Places"
          3. Тап по координатам карандаша
        """
        from pages.edit_bookmark_page import EditBookmarkPage
        edit = EditBookmarkPage(self.driver)

        # Уже открылся автоматически?
        if edit.is_open(timeout=3):
            logger.info("  Edit bookmark открылся автоматически")
            return edit

        self._ensure_foreground()

        # Пробуем нажать карандаш через xpath
        if self.is_element_present(Loc.CARD_EDIT_PENCIL, timeout=4):
            self.click(Loc.CARD_EDIT_PENCIL)
            time.sleep(2)
            return edit

        # Пробуем через тап по координатам карандаша
        if self.is_text_on_screen("My Places", timeout=3):
            logger.info("  Тапаем карандаш по координатам")
            self.safe_tap(*Loc.CARD_EDIT_PENCIL_COORDS, pause=2)
            return edit

        logger.warning("  Не удалось открыть Edit bookmark")
        return edit

    def get_title(self) -> str:
        try:
            return self.get_text(Loc.CARD_TITLE)
        except Exception:
            return "Unknown"

    # Алиасы для совместимости
    def tap_add_bookmark(self) -> "EditBookmarkPage":
        self.tap_bookmark_btn()
        return self.open_edit_bookmark()

    def tap_edit_bookmark(self) -> "EditBookmarkPage":
        return self.open_edit_bookmark()

    def tap_remove_bookmark(self) -> None:
        self.remove_bookmark_with_confirmation()

    def is_add_bookmark_button_visible(self) -> bool:
        return not self.is_bookmarked()

    def is_edit_bookmark_button_visible(self) -> bool:
        return self.is_bookmarked()
