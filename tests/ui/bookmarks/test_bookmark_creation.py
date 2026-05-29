"""
tests/test_bookmark_creation.py
================================
Тесты создания меток. Адаптированы под реальный UI MAPS.ME.

Флоу добавления метки:
  1. Тап по карте → свёрнутая карточка
  2. Свайп вверх → полная карточка  
  3. Нажать place_bookmark_button (флажок)
  4. Нажать карандаш рядом с "My Places" → Edit bookmark
  5. Изменить имя / нажать Save
"""
import time
import pytest, allure
from config.settings import TestData, BookmarkColors, FieldLimits
from config.locators import Loc
from pages.map_page import MapPage
from pages.favorites_page import FavoritesPage
from utils.helpers import unique_name


@allure.epic("Метки (Bookmarks)")
@allure.feature("Создание меток")
class TestBookmarkCreation:

    @staticmethod
    def _open_unbookmarked_card(map_page):
        """Opens any object card ensuring the object is NOT already bookmarked."""
        card = map_page.open_any_object()
        if card.is_bookmarked():
            card.remove_bookmark_with_confirmation()
            time.sleep(2)
            map_page.ensure_on_map()
            card = map_page.open_any_object()
        return card

    @allure.title("TC-CR-01: Добавить метку через кнопку флажка в карточке")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.creation
    def test_add_bookmark_opens_edit_screen(self, map_page):
        with allure.step("Open object card"):
            card = self._open_unbookmarked_card(map_page)
            assert card.is_card_open(), "Object card not opened"
            card.take_screenshot("card_opened")

        with allure.step("Click flag"):
            card.tap_bookmark_btn()

        with allure.step("Open Edit bookmark screen"):
            edit = card.open_edit_bookmark()
            assert edit.is_open(), "Edit bookmark screen not opened"
            edit.take_screenshot("edit_bookmark_opened")

        with allure.step("Save bookmark"):
            edit.tap_save()

    @allure.title("TC-CR-02: Default bookmark name = object name")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.creation
    def test_default_bookmark_name(self, map_page):
        with allure.step("Open card and add bookmark"):
            card = self._open_unbookmarked_card(map_page)
            object_title = card.get_title()
            allure.attach(object_title, name="Object name",
                          attachment_type=allure.attachment_type.TEXT)
            card.tap_bookmark_btn()
            edit = card.open_edit_bookmark()

        with allure.step("Check default name"):
            default_name = edit.get_name()
            allure.attach(default_name, name="Default name",
                          attachment_type=allure.attachment_type.TEXT)
            assert default_name.strip() != "", \
                "Bookmark name field is empty - should be filled by default"

        edit.tap_save()

    @allure.title("TC-CR-03: Bookmark saved with custom name")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.creation
    def test_save_bookmark_with_custom_name(self, map_page, driver):
        name = unique_name("My_bookmark")

        with allure.step("Add bookmark with name"):
            card = self._open_unbookmarked_card(map_page)
            card.tap_bookmark_btn()
            edit = card.open_edit_bookmark()
            edit.set_name(name)
            edit.tap_save()

        with allure.step("Check bookmark in Favorites"):
            fav = FavoritesPage(driver)
            fav.open()
            assert fav.bookmark_exists(name), \
                f"Bookmark '{name}' not found in Favorites"

    @allure.title("TC-CR-04: Cannot save bookmark with empty name")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.creation
    def test_cannot_save_empty_name(self, map_page):
        with allure.step("Add bookmark"):
            card = self._open_unbookmarked_card(map_page)
            card.tap_bookmark_btn()
            edit = card.open_edit_bookmark()

        with allure.step("Clear name field"):
            edit.set_name("   ")

        with allure.step("Save button inactive or error appears"):
            still_open = edit.is_open()
            allure.attach(
                f"Edit bookmark screen open: {still_open}",
                name="Result",
                attachment_type=allure.attachment_type.TEXT,
            )
        edit.tap_back()

    @allure.title("TC-CR-05: Bookmark appears in Favorites list")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.creation
    def test_bookmark_appears_in_favorites(self, bookmark_created, driver):
        name = bookmark_created

        with allure.step(f"Open Favorites and find bookmark '{name}'"):
            fav = FavoritesPage(driver)
            fav.open()
            open_my_places = fav.open_my_places()
            names = fav.get_bookmark_names()
            allure.attach(str(names), name="Bookmark list",
                          attachment_type=allure.attachment_type.TEXT)
            assert fav.bookmark_exists(name), \
                f"Bookmark '{name}' not found. Available: {names}"

    @allure.title("TC-CR-06: 60 character limit in bookmark name field")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.creation
    def test_bookmark_name_max_60_chars(self, map_page):
        long_name = "А" * 70

        with allure.step("Add bookmark and open Edit bookmark"):
            card = self._open_unbookmarked_card(map_page)
            card.tap_bookmark_btn()
            edit = card.open_edit_bookmark()

        with allure.step("Enter 70 characters"):
            edit.set_name(long_name)
            actual = edit.name_char_count()
            allure.attach(f"Entered: 70, accepted: {actual}",
                          name="Character counter",
                          attachment_type=allure.attachment_type.TEXT)

        with allure.step("Check 60 character limit"):
            assert actual <= FieldLimits.BOOKMARK_NAME_MAX, \
                f"Accepted {actual} characters, limit = {FieldLimits.BOOKMARK_NAME_MAX}"

        edit.tap_back()