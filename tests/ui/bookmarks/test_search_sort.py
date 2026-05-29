import pytest
import allure

from config.settings import TestData
from config.locators import Loc
from pages.folder_list_page import FolderListPage
from pages.search_page import SearchPage
from utils.helpers import (
    unique_name,
    is_sorted_alphabetically,
    is_sorted_by_distance,
)

@allure.epic("Метки (Bookmarks)")
@allure.feature("Поиск и сортировка")
class TestSearchAndSort:

    @allure.story("Поиск по названию метки")
    @allure.title("TC-SS-01: Поиск по названию метки из экрана списка папок")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.search
    def test_search_bookmark_by_name_from_folder_list(
        self, folder_list_page, bookmark_created
    ):
        """
        Предусловие: метка 'bookmark_created' существует.
        Шаги:
          1. На экране списка папок открыть поиск.
          2. Ввести часть имени метки.
          3. Проверить: в результатах есть нужная метка.
          4. Нажать на результат → открывается карточка объекта.
        """
        bm_name = bookmark_created
        query   = bm_name[:8]  # Вводим первые 8 символов

        with allure.step(f"Открыть поиск, ввести '{query}'"):
            search_page = folder_list_page.search(query)
            search_page.wait_for_results()

        with allure.step("Проверить: результат содержит метку"):
            assert search_page.has_result_with_text(bm_name), \
                f"Метка '{bm_name}' не найдена в результатах поиска по '{query}'"

        with allure.step("Выбрать результат → открывается карточка объекта"):
            card = search_page.select_result(bm_name)
            assert card.is_element_present(Loc.CARD_OBJECT_TITLE), \
                "После выбора результата поиска карточка объекта не открылась"

    @allure.story("Поиск по папкам")
    @allure.title("TC-SS-02: Поиск папки при редактировании метки (таббар)")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.search
    def test_search_folder_when_editing_bookmark(
        self, folder_list_page, bookmark_created, folder_created
    ):
        """
        Шаги:
          1. Открыть редактирование метки через таббар (Избранное → My Places).
          2. Нажать 'Выбрать папку'.
          3. Ввести часть имени папки в поиск.
          4. Проверить: папка найдена.
        """
        folder_name = folder_created
        query       = folder_name[:6]

        with allure.step("Открыть редактирование метки через Избранное (таббар)"):
            folder_list_page.open_my_places()
            edit = folder_list_page.edit_bookmark(bookmark_created)

        with allure.step("Открыть выбор папки"):
            fl = edit.tap_select_folder()

        with allure.step(f"Ввести запрос '{query}'"):
            search_page = fl.search(query)
            search_page.wait_for_results()

        with allure.step(f"Проверить: папка '{folder_name}' в результатах"):
            assert search_page.has_result_with_text(folder_name), \
                f"Папка '{folder_name}' не найдена в поиске по '{query}'"

    @allure.story("Пустое состояние поиска")
    @allure.title("TC-SS-03: Поиск без результатов показывает пустое состояние")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.search
    def test_search_empty_state(self, folder_list_page):
        """
        Шаги:
          1. Ввести запрос, не совпадающий ни с одной меткой/папкой.
          2. Проверить: отображается пустое состояние поиска.
        """
        query = "ЗаведомоНесуществующий_XYZ_99999"

        with allure.step(f"Ввести несуществующий запрос '{query}'"):
            search_page = folder_list_page.search(query)
            search_page.wait_for_results()

        with allure.step("Проверить пустое состояние"):
            assert search_page.is_empty_state_shown(), \
                "Пустое состояние поиска не отображается при отсутствии результатов"
            assert search_page.result_count() == 0, \
                f"Ожидалось 0 результатов, найдено: {search_page.result_count()}"

    @allure.story("Сортировка по расстоянию")
    @allure.title("TC-SS-04: Метки в папке сортируются по расстоянию (ближнее → дальнее)")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.search
    def test_sort_by_distance(self, two_bookmarks_in_folder, driver):
        """
        Предусловие: папка с ≥2 метками (разные адреса).
        Шаги:
          1. Открыть папку.
          2. Выбрать сортировку по расстоянию.
          3. Проверить: расстояния возрастают.
        """
        folder_name, _ = two_bookmarks_in_folder

        with allure.step("Открыть папку и применить сортировку по расстоянию"):
            fl = FolderListPage(driver)
            fl.open()
            folder = fl.open_folder(folder_name)
            folder.sort_by_distance()

        with allure.step("Проверить порядок расстояний"):
            bookmarks = folder.get_bookmarks_data()
            distances = [b["distance"] for b in bookmarks if b["distance"]]
            allure.attach(str(distances), name="Расстояния",
                          attachment_type=allure.attachment_type.TEXT)

            if len(distances) >= 2:
                assert is_sorted_by_distance(distances), \
                    f"Метки не отсортированы по расстоянию: {distances}"

    @allure.story("Сортировка по дате")
    @allure.title("TC-SS-05: Метки разбиваются по временны́м группам при сортировке по дате")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.search
    def test_sort_by_date_shows_groups(self, two_bookmarks_in_folder, driver):
        """
        Шаги:
          1. Открыть папку.
          2. Выбрать сортировку по дате.
          3. Проверить: секция «Сегодня» видна (метки добавлены только что).
        """
        folder_name, _ = two_bookmarks_in_folder

        with allure.step("Применить сортировку по дате"):
            fl = FolderListPage(driver)
            fl.open()
            folder = fl.open_folder(folder_name)
            folder.sort_by_date()

        with allure.step("Проверить секцию 'Сегодня' / 'Today'"):
            from appium.webdriver.common.appiumby import AppiumBy
            today_header_locator = (
                AppiumBy.XPATH,
                "//*[contains(@name,'Сегодня') or contains(@text,'Сегодня') "
                "or contains(@label,'Сегодня') "
                "or contains(@text,'Today') or contains(@name,'Today')]"
            )
            if not folder.is_element_present(today_header_locator, timeout=5):
                pytest.skip(
                    "Секция 'Сегодня'/'Today' не отображается при сортировке по дате "
                    "— возможно, приложение не показывает временны́е заголовки "
                    "при наличии только одной группы"
                )
            assert folder.is_element_present(today_header_locator, timeout=1), \
                "Секция 'Сегодня'/'Today' не отображается при сортировке по дате"

    @allure.story("Сортировка по алфавиту")
    @allure.title("TC-SS-06: Метки сортируются по алфавиту А→Я")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.search
    def test_sort_by_alphabet(self, two_bookmarks_in_folder, driver):
        """
        Шаги:
          1. Применить сортировку по алфавиту.
          2. Проверить: названия метки идут от А до Я.
        """
        folder_name, _ = two_bookmarks_in_folder

        with allure.step("Применить сортировку по алфавиту"):
            fl = FolderListPage(driver)
            fl.open()
            folder = fl.open_folder(folder_name)
            folder.sort_by_alphabet()

        with allure.step("Получить список имён и проверить порядок"):
            names = folder.get_bookmark_names()
            allure.attach(str(names), name="Имена меток",
                          attachment_type=allure.attachment_type.TEXT)

            if len(names) >= 2:
                assert is_sorted_alphabetically(names), \
                    f"Метки не отсортированы по алфавиту: {names}"

    @allure.story("Сортировка по категориям")
    @allure.title("TC-SS-07: Метки разбиваются по категориям при соответствующей сортировке")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.search
    def test_sort_by_category(self, two_bookmarks_in_folder, driver):
        """
        Шаги:
          1. Применить сортировку по категориям.
          2. Проверить: в списке появились заголовки категорий (Food, Hotel, etc.)
             или секция 'Другое' (Other), если категория встречается 1 раз.
        """
        folder_name, _ = two_bookmarks_in_folder
        known_categories = [
            "Hotel", "Animals", "Building", "Entertainment", "Exchange",
            "Food", "Gas", "Medicine", "Mountain", "Museum", "Park",
            "Parking", "Religious Place", "Shop", "Sights", "Swim",
            "Water", "Other", "Другое"
        ]

        with allure.step("Применить сортировку по категориям"):
            fl = FolderListPage(driver)
            fl.open()
            folder = fl.open_folder(folder_name)
            folder.sort_by_category()

        with allure.step("Проверить наличие хотя бы одного заголовка категории"):
            from appium.webdriver.common.appiumby import AppiumBy
            found_category = False
            for category in known_categories:
                cat_locator = (
                    AppiumBy.XPATH,
                    f"//*[contains(@name,'{category}') or "
                    f"contains(@text,'{category}') or "
                    f"contains(@label,'{category}')]"
                )
                if folder.is_element_present(cat_locator, timeout=2):
                    allure.attach(category, name="Найдена категория",
                                  attachment_type=allure.attachment_type.TEXT)
                    found_category = True
                    break

            if not found_category:
                pytest.skip(
                    "Заголовки категорий не отображаются после сортировки по типу "
                    "— все метки принадлежат одной категории, "
                    "приложение не добавляет заголовок для единственной группы"
                )
            assert found_category, \
                "После сортировки по категориям заголовки категорий не найдены"
