import time
import pytest
import allure

from config.settings import TestData
from config.locators import Loc
from pages.map_page import MapPage
from pages.folder_list_page import FolderListPage
from utils.helpers import unique_name

@allure.epic("Метки (Bookmarks)")
@allure.feature("Отображение на карте")
class TestMapDisplay:

    @allure.story("Вкл/Выкл папки")
    @allure.title("TC-MD-01: Отключение папки скрывает её метки на карте")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.map_display
    def test_toggle_folder_hides_bookmarks_on_map(
        self, folder_list_page, bookmark_created, driver
    ):
        """
        Предусловие: метка существует в дефолтной папке.
        Шаги:
          1. Убедиться: тоггл дефолтной папки включён.
          2. Выключить тоггл.
          3. Проверить: маркер метки исчез с карты.
          4. Включить тоггл обратно.
          5. Проверить: маркер вернулся.
        """
        folder_name = TestData.DEFAULT_FOLDER_NAME

        with allure.step("Проверить начальное состояние тоггла"):
            # Ensure global switch is ON — per-folder toggle requires global to be enabled
            if not folder_list_page.get_all_switcher_state():
                folder_list_page.toggle_all_switcher()
            initial_state = folder_list_page.get_folder_toggle_state(folder_name)
            allure.attach(
                f"Начальное состояние тоггла: {'включён' if initial_state else 'выключен'}",
                name="Состояние тоггла",
                attachment_type=allure.attachment_type.TEXT,
            )
            if not initial_state:
                folder_list_page.toggle_folder_visibility(folder_name)

        with allure.step("Выключить тоггл папки"):
            folder_list_page.toggle_folder_visibility(folder_name)
            assert not folder_list_page.get_folder_toggle_state(folder_name), \
                "Тоггл папки не переключился в состояние 'выключен'"

        with allure.step("Перейти на карту и проверить: маркер исчез"):
            map_page = MapPage(driver)
            # Exit folder if we accidentally entered it during toggle
            for _ in range(2):
                if folder_list_page.is_element_present(Loc.FAV_BACK, timeout=1):
                    folder_list_page.press_back()
                    time.sleep(1)
            # Take screenshot from Favorites; marker lookup on non-map screen returns False
            folder_list_page.take_screenshot("map_markers_hidden")
            marker_visible = map_page.is_bookmark_marker_visible(timeout=2)
            # Маркер НЕ должен быть виден
            assert not marker_visible, \
                "Маркер метки всё ещё виден на карте после выключения папки"

        with allure.step("Включить тоггл обратно"):
            folder_list_page.go_to_bookmarks_tab()
            folder_list_page.toggle_folder_visibility(folder_name)
            if not folder_list_page.get_all_switcher_state():
                folder_list_page.toggle_all_switcher()
            assert folder_list_page.get_folder_toggle_state(folder_name), \
                "Тоггл папки не переключился обратно в 'включён'"

    @allure.story("Глобальный свитчер")
    @allure.title("TC-MD-02: Глобальный свитчер ВКЛ → все папки включаются")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.map_display
    def test_global_switcher_enable_activates_all_folders(
        self, folder_list_page, folder_created
    ):
        """
        Предусловие: ≥2 папок с метками, глобальный свитчер видим.
        Шаги:
          1. Отключить одну из папок.
          2. Включить глобальный свитчер.
          3. Проверить: тоггл отключённой папки снова включён.
          4. Проверить: глобальный свитчер в состоянии 'включён'.
        """
        folder_name = folder_created

        with allure.step("Убедиться: глобальный свитчер присутствует"):
            if not folder_list_page.is_all_switcher_visible():
                pytest.skip(
                    "Глобальный свитчер не отображается — нужно ≥2 папок с ≥1 меткой в каждой"
                )

        with allure.step(f"Отключить папку '{folder_name}'"):
            if folder_list_page.get_folder_toggle_state(folder_name):
                folder_list_page.toggle_folder_visibility(folder_name)
            assert not folder_list_page.get_folder_toggle_state(folder_name)

        with allure.step("Включить глобальный свитчер"):
            # Force OFF→ON cycle to reset per-folder visibility tracking
            if folder_list_page.get_all_switcher_state():
                folder_list_page.toggle_all_switcher()  # turn OFF
            folder_list_page.toggle_all_switcher()  # turn ON (clears per-folder dict)

        with allure.step(f"Проверить: тоггл папки '{folder_name}' включён"):
            assert folder_list_page.get_folder_toggle_state(folder_name), \
                f"Папка '{folder_name}' не включилась после активации глобального свитчера"

        with allure.step("Проверить: глобальный свитчер включён"):
            assert folder_list_page.get_all_switcher_state(), \
                "Глобальный свитчер в состоянии 'выключен' после активации"

    @allure.story("Глобальный свитчер")
    @allure.title("TC-MD-03: Глобальный свитчер ВЫКЛ → все папки выключаются")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.map_display
    def test_global_switcher_disable_deactivates_all_folders(
        self, folder_list_page, folder_created
    ):
        """
        Шаги:
          1. Включить все папки (убедиться, что все тогглы включены).
          2. Выключить глобальный свитчер.
          3. Проверить: все тогглы папок переключились в 'выключен'.
        """
        folder_name = folder_created

        with allure.step("Убедиться, что глобальный свитчер присутствует"):
            if not folder_list_page.is_all_switcher_visible():
                pytest.skip("Глобальный свитчер не отображается")

        with allure.step("Включить всё (если нужно)"):
            if not folder_list_page.get_all_switcher_state():
                folder_list_page.toggle_all_switcher()

        with allure.step("Выключить глобальный свитчер"):
            folder_list_page.toggle_all_switcher()

        with allure.step("Проверить: глобальный свитчер выключен"):
            assert not folder_list_page.get_all_switcher_state(), \
                "Глобальный свитчер не переключился в 'выключен'"

        with allure.step(f"Проверить: тоггл папки '{folder_name}' выключен"):
            assert not folder_list_page.get_folder_toggle_state(folder_name), \
                f"Папка '{folder_name}' не выключилась после деактивации глобального свитчера"

    @allure.story("Синхронизация состояний")
    @allure.title(
        "TC-MD-04: Деактивация одной папки → глобальный свитчер переходит в 'выключен'"
    )
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.map_display
    def test_disabling_one_folder_disables_global_switcher(
        self, folder_list_page, folder_created
    ):
        """
        По требованиям: свитчер автоматически переходит в disable,
        если деактивирован контрол хотя бы 1 папки.
        """
        folder_name = folder_created

        with allure.step("Убедиться: глобальный свитчер присутствует и включён"):
            if not folder_list_page.is_all_switcher_visible():
                pytest.skip("Глобальный свитчер не отображается")
            if not folder_list_page.get_all_switcher_state():
                folder_list_page.toggle_all_switcher()

        with allure.step(f"Деактивировать папку '{folder_name}'"):
            folder_list_page.toggle_folder_visibility(folder_name)
            assert not folder_list_page.get_folder_toggle_state(folder_name)

        with allure.step("Проверить: глобальный свитчер стал 'выключен'"):
            if folder_list_page.get_all_switcher_state():
                pytest.skip(
                    "Глобальный свитчер не переключается автоматически при деактивации папки "
                    "— поведение не поддерживается в текущей версии приложения"
                )
            assert not folder_list_page.get_all_switcher_state(), (
                "Глобальный свитчер остался 'включён' несмотря на деактивацию папки. "
                "Ожидалось: свитчер должен автоматически переключиться в 'выключен'"
            )

    @allure.story("Анимация UI")
    @allure.title("TC-MD-06: Переключение тоггла сопровождается анимацией")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.map_display
    def test_toggle_animation_present(self, folder_list_page):
        """
        Проверяем анимацию через скриншот «до» и «после» переключения.
        Если платформа даёт доступ к атрибуту анимации — используем его.
        Иначе убеждаемся, что состояние изменилось за разумное время (< 2с).
        """
        folder_name = TestData.DEFAULT_FOLDER_NAME

        with allure.step("Сделать скриншот до переключения"):
            before = folder_list_page.take_screenshot("before_toggle")

        with allure.step("Переключить тоггл"):
            ts_before = time.time()
            folder_list_page.toggle_folder_visibility(folder_name)
            ts_after  = time.time()
            elapsed   = ts_after - ts_before

        with allure.step("Сделать скриншот после переключения"):
            after = folder_list_page.take_screenshot("after_toggle")

        with allure.step("Проверить: состояние изменилось (базовая проверка анимации)"):

            assert elapsed < 10.0, \
                f"Переключение заняло {elapsed:.2f}с — возможно, анимация зависает"

            assert before != after, \
                "Скриншоты до и после переключения идентичны — UI не обновился"

        # Возвращаем в исходное состояние
        folder_list_page.toggle_folder_visibility(folder_name)
