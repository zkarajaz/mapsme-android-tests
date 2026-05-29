"""
tests/test_bookmark_edit.py
============================
Тесты редактирования меток.

АРХИТЕКТУРА:
  - СОЗДАНИЕ метки  → fixture bookmark_created (через КАРТУ)
  - РЕДАКТИРОВАНИЕ  → через ТАББАР: Favorites → My Places → Edit
"""
import pytest
import allure

from config.settings import TestData, FieldLimits
from config.locators import Loc
from pages.favorites_page import FavoritesPage
from pages.edit_bookmark_page import EditBookmarkPage
from utils.helpers import unique_name, generate_string


def _open_edit_via_tabbar(driver, bookmark_name: str) -> EditBookmarkPage:
    """
    Вспомогательная функция: открывает экран Edit bookmark через таббар.
    Favorites → My Places → tap '...' → Edit
    """
    fav = FavoritesPage(driver)
    fav.open()
    fav.open_my_places()
    return fav.edit_bookmark(bookmark_name)


@allure.epic("Метки (Bookmarks)")
@allure.feature("Редактирование меток")
class TestBookmarkEdit:

    @allure.story("Изменение названия")
    @allure.title("TC-ED-01: Изменение названия метки через Избранное (таббар)")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.edit
    def test_edit_bookmark_name(self, bookmark_created, driver):
        """
        Предусловие: метка создана fixture bookmark_created (через карту).
        Шаги:
          1. Открыть Избранное → My Places → редактировать метку (таббар).
          2. Изменить название.
          3. Сохранить.
          4. Проверить новое название в папке.
        """
        new_name = unique_name("Изменённая_метка")

        with allure.step("Открыть редактирование через Избранное (таббар)"):
            edit = _open_edit_via_tabbar(driver, bookmark_created)
            edit.take_screenshot("edit_open")

        with allure.step(f"Изменить название на '{new_name}'"):
            edit.set_name(new_name)

        with allure.step("Сохранить"):
            edit.tap_save()

        with allure.step("Проверить новое название в папке через Избранное"):
            fav = FavoritesPage(driver)
            fav.open()
            fav.open_my_places()
            assert fav.bookmark_exists(new_name), \
                f"Метка с новым названием '{new_name}' не найдена в папке"

    @allure.story("Изменение описания")
    @allure.title("TC-ED-02: Изменение описания метки через Избранное (таббар)")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.edit
    def test_edit_bookmark_description(self, bookmark_created, driver):
        """
        Шаги:
          1. Открыть редактирование через таббар.
          2. Ввести описание (~100 символов).
          3. Сохранить.
        """
        description = "Описание тестовой метки. " * 4  # ~100 символов

        with allure.step("Открыть редактирование через Избранное (таббар)"):
            edit = _open_edit_via_tabbar(driver, bookmark_created)

        with allure.step("Ввести описание"):
            edit.set_description(description)
            actual_desc = edit.get_description()
            allure.attach(actual_desc, name="Введённое описание",
                          attachment_type=allure.attachment_type.TEXT)

        with allure.step("Сохранить"):
            edit.tap_save()

    @allure.story("Изменение цвета")
    @allure.title("TC-ED-03: Изменение цвета метки через Избранное (таббар)")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.edit
    def test_edit_bookmark_color_becomes_default(self, bookmark_created, driver):
        """
        Шаги:
          1. Открыть редактирование через таббар.
          2. Открыть палитру цветов → выбрать второй цвет.
          3. Сохранить.
          4. Зафиксировать выбранный цвет в отчёте.
        """
        with allure.step("Открыть редактирование через Избранное (таббар)"):
            edit = _open_edit_via_tabbar(driver, bookmark_created)

        with allure.step("Открыть палитру и выбрать второй цвет"):
            edit.open_color_picker()
            colors = edit.find_elements(Loc.EDIT_BM_COLOR_CELL)
            if len(colors) >= 2:
                second_color_label = (colors[1].get_attribute("value") or
                                      colors[1].get_attribute("label") or "unknown")
                colors[1].click()
                edit.wait_for_animation()
            else:
                second_color_label = "palette not found"
                allure.attach("Палитра цветов недоступна",
                              name="Примечание",
                              attachment_type=allure.attachment_type.TEXT)
            # Color picker may open a separate screen — always return to Edit
            if not edit.is_open(timeout=3):
                edit.press_back()
                edit.wait_for_animation()

        allure.attach(second_color_label, name="Выбранный цвет",
                      attachment_type=allure.attachment_type.TEXT)

        with allure.step("Сохранить"):
            edit.tap_save()

    @allure.story("Перемещение в другую папку")
    @allure.title("TC-ED-04: Перемещение метки в другую папку через Избранное (таббар)")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.edit
    def test_move_bookmark_to_another_folder(
        self, bookmark_created, folder_created, driver
    ):
        """
        Предусловие: метка в My Places, папка folder_created существует.
        Шаги:
          1. Открыть редактирование через таббар.
          2. Выбрать папку folder_created.
          3. Сохранить.
          4. Проверить: метка появилась в folder_created.
        """
        folder_name = folder_created

        with allure.step("Открыть редактирование через Избранное (таббар)"):
            edit = _open_edit_via_tabbar(driver, bookmark_created)

        with allure.step(f"Нажать 'Выбрать папку' → выбрать '{folder_name}'"):
            fl = edit.tap_select_folder()
            fl.open_folder(folder_name)

        with allure.step("Сохранить"):
            edit.tap_save()

        with allure.step(f"Проверить: метка в папке '{folder_name}'"):
            fav = FavoritesPage(driver)
            fav.open()
            fav.open_folder(folder_name)
            assert fav.bookmark_exists(bookmark_created), \
                f"Метка не найдена в папке '{folder_name}'"

    @allure.story("Возврат на предыдущий экран")
    @allure.title("TC-ED-05: После сохранения — возврат на экран Избранного")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.edit
    def test_back_navigation_after_save(self, bookmark_created, driver):
        """
        Шаги:
          1. Открыть Избранное → My Places → редактировать метку.
          2. Изменить название, сохранить.
          3. Проверить: экран Избранного виден (не карта, не главное меню).
        """
        with allure.step("Открыть Избранное → My Places → редактирование"):
            fav = FavoritesPage(driver)
            fav.open()
            fav.open_my_places()
            edit = fav.edit_bookmark(bookmark_created)

        with allure.step("Изменить название и сохранить"):
            edit.set_name(unique_name("Метка_возврат"))
            edit.tap_save()

        with allure.step("Проверить возврат на экран Избранного"):
            assert fav.is_open(), \
                "После сохранения не произошёл возврат на экран Избранного"

    @allure.story("Лимит символов в названии")
    @allure.title("TC-ED-06: Название метки ограничено 60 символами (таббар)")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.edit
    def test_bookmark_name_max_length(self, bookmark_created, driver):
        """
        Шаги:
          1. Открыть редактирование через таббар.
          2. Ввести строку из 65 символов.
          3. Проверить: фактически введено не более 60 символов.
        """
        long_name = generate_string(65, "Я")

        with allure.step("Открыть редактирование через Избранное (таббар)"):
            edit = _open_edit_via_tabbar(driver, bookmark_created)

        with allure.step(f"Ввести строку из {len(long_name)} символов"):
            edit.set_name(long_name)
            actual_length = edit.name_field_char_count()
            allure.attach(
                f"Введено: {len(long_name)}, принято: {actual_length}",
                name="Счётчик символов",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("Проверить: не более 60 символов"):
            assert actual_length <= FieldLimits.BOOKMARK_NAME_MAX, (
                f"Поле приняло {actual_length} символов, "
                f"лимит = {FieldLimits.BOOKMARK_NAME_MAX}"
            )

        edit.tap_save()
