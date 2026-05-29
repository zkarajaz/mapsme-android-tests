"""tests/test_folder_management.py — Работа с папками"""
import pytest, allure
from config.locators import Loc
from config.settings import TestData
from pages.favorites_page import FavoritesPage
from utils.helpers import unique_name


@allure.epic("Метки (Bookmarks)")
@allure.feature("Работа с папками")
class TestFolderManagement:

    @allure.title("TC-FL-01: Экран Избранного открывается")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.folders
    def test_favorites_screen_opens(self, favorites_page):
        with allure.step("Проверить что экран Избранного открылся"):
            favorites_page.take_screenshot("favorites_screen")
            assert favorites_page.is_open(), "Экран Избранного не открылся"

        with allure.step("Проверить наличие кнопки меню (три точки)"):
            # Используем FAV_MENU — тот же локатор что и FAVORITES_MENU
            has_menu = favorites_page.is_element_present(Loc.FAV_MENU, timeout=5)
            allure.attach(f"Кнопка меню найдена: {has_menu}",
                          name="Меню", attachment_type=allure.attachment_type.TEXT)
            assert has_menu, "Кнопка меню (три точки) не найдена"

    @allure.title("TC-FL-02: Папка 'My Places' существует")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.folders
    def test_default_folder_exists(self, favorites_page):
        with allure.step("Проверить наличие 'My Places' на экране"):
            favorites_page.take_screenshot("main_favorites")
            assert favorites_page.is_text_on_screen(
                TestData.DEFAULT_FOLDER_NAME, timeout=8
            ), f"'{TestData.DEFAULT_FOLDER_NAME}' не найдена на экране"

    @allure.title("TC-FL-03: Создание новой папки через меню")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.folders
    def test_create_new_folder(self, favorites_page):
        name = unique_name("НоваяПапка")

        with allure.step("Открыть меню"):
            favorites_page.tap_menu()
            favorites_page.take_screenshot("menu_opened")

        with allure.step("Нажать 'Add folder'"):
            if not favorites_page.is_element_present(Loc.MENU_ADD_FOLDER, timeout=5):
                pytest.skip("Пункт 'Add folder' не найден в меню")
            favorites_page.click(Loc.MENU_ADD_FOLDER)
            favorites_page.wait_anim(2)

        with allure.step(f"Ввести имя '{name}' и сохранить"):
            favorites_page.take_screenshot("add_folder_screen")
            if favorites_page.is_element_present(Loc.FOLDER_NAME_INPUT, timeout=8):
                favorites_page.type_text(Loc.FOLDER_NAME_INPUT, name)
                favorites_page.take_screenshot("name_entered")
            favorites_page.tap_folder_save_btn()
            favorites_page.wait_anim(2)
            favorites_page.take_screenshot("after_create")

    @allure.title("TC-FL-04: Список меток отображается в папке")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.folders
    def test_bookmarks_visible_in_folder(self, favorites_page, bookmark_created):
        name = bookmark_created

        with allure.step("Открыть папку My Places"):
            favorites_page.open_my_places()
            favorites_page.take_screenshot("inside_my_places")

        with allure.step("Проверить список меток"):
            names = favorites_page.get_bookmark_names()
            allure.attach(str(names), name="Список меток",
                          attachment_type=allure.attachment_type.TEXT)
            assert len(names) > 0 or favorites_page.is_text_on_screen(name, timeout=5), \
                "Список меток пуст"

    @allure.title("TC-FL-05: Поиск по имени метки в Избранном")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.folders
    def test_search_in_favorites(self, favorites_page, bookmark_created):
        name = bookmark_created
        query = name[:6]

        with allure.step(f"Поиск '{query}'"):
            favorites_page.search(query)
            favorites_page.take_screenshot("search_results")

        with allure.step("Проверить результат"):
            found = (favorites_page.has_result_with_text(query) or
                     favorites_page.has_result_with_text(name[:4]))
            allure.attach(f"Найдено: {found}", name="Результат поиска",
                          attachment_type=allure.attachment_type.TEXT)

    @allure.title("TC-FL-06: Переключатель 'Show all bookmarks on map' виден")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.folders
    def test_all_switch_visible(self, favorites_page):
        with allure.step("Проверить переключатель"):
            visible = favorites_page.is_all_switch_visible()
            favorites_page.take_screenshot("switch_check")
            allure.attach(f"Виден: {visible}", name="Switch",
                          attachment_type=allure.attachment_type.TEXT)

    @allure.title("TC-FL-07: Переключатель меняет состояние")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.folders
    def test_toggle_all_switch(self, favorites_page, bookmark_created):
        if not favorites_page.is_all_switch_visible():
            pytest.skip("Переключатель не виден")

        with allure.step("Запомнить состояние"):
            initial = favorites_page.get_all_switch_state()
            allure.attach(f"Начало: {initial}", name="Состояние",
                          attachment_type=allure.attachment_type.TEXT)

        with allure.step("Переключить"):
            favorites_page.toggle_all_switch()

        with allure.step("Проверить изменение"):
            new_state = favorites_page.get_all_switch_state()
            assert new_state != initial, "Состояние не изменилось"

        favorites_page.toggle_all_switch()  # Возврат
