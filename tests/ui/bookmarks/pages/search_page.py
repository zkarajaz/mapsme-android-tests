"""
pages/search_page.py
====================
Страница результатов поиска внутри Избранного.
Наследует FavoritesPage и добавляет методы для работы с результатами поиска.
"""
import time, logging
from pages.favorites_page import FavoritesPage
from config.locators import Loc

logger = logging.getLogger(__name__)


class SearchPage(FavoritesPage):

    def wait_for_results(self, timeout: float = 3) -> "SearchPage":
        """Ожидает появления результатов поиска."""
        time.sleep(min(timeout * 0.5, 2))
        return self

    def select_result(self, name: str):
        """Выбирает результат поиска по имени. Возвращает ObjectCardPage."""
        from pages.object_card_page import ObjectCardPage
        self.click_text(name)
        time.sleep(2)
        return ObjectCardPage(self.driver)

    def is_empty_state_shown(self) -> bool:
        """Возвращает True если поиск не нашёл результатов."""
        return (
            self.is_text_on_screen("No results",          timeout=3) or
            self.is_text_on_screen("Nothing found",       timeout=3) or
            self.is_text_on_screen("Ничего не найдено",   timeout=3) or
            self.is_text_on_screen("No bookmarks found",  timeout=3) or
            self.result_count() == 0
        )
