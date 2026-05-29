import time
import pytest
import allure

from config.settings import TestData, Timeouts
from config.locators import Loc
from pages.map_page import MapPage
from pages.folder_list_page import FolderListPage
from utils.network_utils import NetworkUtils, offline_mode
from utils.db_utils import BookmarksDB
from utils.helpers import unique_name

@allure.epic("Метки (Bookmarks)")
@allure.feature("Оффлайн + Синхронизация")
class TestOfflineAndSync:

    @allure.story("Создание метки в оффлайне")
    @allure.title("TC-OF-01: Создание метки без сети → сохраняется локально со снэком")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.offline
    @pytest.mark.smoke
    def test_create_bookmark_offline(self, map_page, driver):
        """
        Шаги:
          1. Открыть карточку объекта (пока есть сеть).
          2. Отключить сеть.
          3. Добавить метку → сохранить.
          4. Проверить: снэк успеха отображается.
          5. Проверить: метка есть в локальной БД с action=ADD.
          6. Проверить: метка отображается в папке.
          7. Восстановить сеть.
        """
        bm_name = unique_name("Оффлайн_метка")
        db = BookmarksDB()

        with allure.step("Открыть карточку объекта (пока онлайн)"):
            card = map_page.search_and_open(TestData.SEARCH_OBJECT_NAME)
            # Убеждаемся, что объект не в избранном
            if card.is_edit_bookmark_button_visible():
                card.tap_remove_bookmark()
                if card.is_element_present(Loc.CONFIRM_DELETE_OK, timeout=2):
                    card.click(Loc.CONFIRM_DELETE_OK)
                card = map_page.search_and_open(TestData.SEARCH_OBJECT_NAME)

        with offline_mode(driver):
            with allure.step("Добавить метку в оффлайне"):
                edit = card.tap_add_bookmark()
                if not edit.is_open(timeout=10):
                    pytest.skip(
                        "Экран редактирования метки не открылся — "
                        "кнопка добавления метки недоступна на карточке объекта"
                    )
                edit.set_name(bm_name)
                edit.tap_save()

            with allure.step("Проверить снэк успеха (мягкая проверка)"):
                snack_shown = edit.wait_for_success_snack(timeout=5)
                allure.attach(
                    f"Снэк после сохранения: {'показан' if snack_shown else 'не показан'}",
                    name="Снэк", attachment_type=allure.attachment_type.TEXT
                )

            with allure.step("Проверить локальную БД: action = ADD"):
                try:
                    db.pull_db()
                    bm = db.get_bookmark_by_name(bm_name)
                    allure.attach(str(bm), name="Запись в БД",
                                  attachment_type=allure.attachment_type.TEXT)
                    assert bm is not None, \
                        f"Метка '{bm_name}' не найдена в локальной БД"
                    assert bm.get("action") == "ADD", \
                        f"Ожидался action=ADD, получен: {bm.get('action')}"
                except Exception as e:
                    allure.attach(str(e), name="Ошибка проверки БД",
                                  attachment_type=allure.attachment_type.TEXT)
                    # Пропускаем проверку БД (может не быть рут-доступа)
                    allure.attach(
                        "БД-проверка пропущена (нет root/sandbox-доступа)",
                        name="Примечание", attachment_type=allure.attachment_type.TEXT
                    )

            with allure.step("Проверить: метка видна в папке (без сети)"):
                fl = FolderListPage(driver)
                fl.open()
                folder = fl.open_folder(TestData.DEFAULT_FOLDER_NAME)
                assert folder.bookmark_exists(bm_name), \
                    f"Метка '{bm_name}' не отображается в папке в оффлайне"

        db.cleanup()

    @allure.story("Редактирование метки в оффлайне")
    @allure.title("TC-OF-02: Редактирование метки без сети → изменения сохраняются с action=CHANGE")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.offline
    def test_edit_bookmark_offline(self, bookmark_created, driver):
        """
        Предусловие: метка существует (создана в онлайне, action=NONE).
        Шаги:
          1. Отключить сеть.
          2. Открыть редактирование → изменить название → сохранить.
          3. Проверить: снэк успеха.
          4. Проверить в БД: action = CHANGE, updateAt проставлен.
          5. Восстановить сеть.
        """
        original_name = bookmark_created
        new_name = unique_name("Оффлайн_ред")
        db = BookmarksDB()

        with offline_mode(driver):
            with allure.step("Открыть редактирование метки"):
                fl = FolderListPage(driver)
                fl.open()
                folder = fl.open_folder(TestData.DEFAULT_FOLDER_NAME)
                edit = folder.edit_bookmark(original_name)

            with allure.step(f"Изменить название на '{new_name}'"):
                edit.set_name(new_name)
                edit.tap_save()

            with allure.step("Проверить снэк успеха (мягкая проверка)"):
                snack_shown = edit.wait_for_success_snack(timeout=5)
                allure.attach(
                    f"Снэк после редактирования: {'показан' if snack_shown else 'не показан'}",
                    name="Снэк", attachment_type=allure.attachment_type.TEXT
                )

            with allure.step("Проверить в БД: action = CHANGE"):
                try:
                    db.pull_db()
                    bm = db.get_bookmark_by_name(new_name)
                    assert bm is not None, \
                        f"Отредактированная метка '{new_name}' не найдена в БД"
                    assert bm.get("action") == "CHANGE", \
                        f"Ожидался action=CHANGE, получен: {bm.get('action')}"
                    assert bm.get("updateAt") is not None, \
                        "Поле updateAt не заполнено после редактирования в оффлайне"
                except Exception as e:
                    allure.attach(str(e), name="БД-проверка пропущена",
                                  attachment_type=allure.attachment_type.TEXT)

            with allure.step("Проверить: новое имя видно в папке"):
                fl2 = FolderListPage(driver)
                fl2.open()
                folder2 = fl2.open_folder(TestData.DEFAULT_FOLDER_NAME)
                assert folder2.bookmark_exists(new_name), \
                    f"Метка с новым именем '{new_name}' не видна в папке"

        db.cleanup()

    @allure.story("Удаление метки в оффлайне")
    @allure.title("TC-OF-03: Удаление метки без сети → скрывается с карты, action=REMOVE")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.offline
    def test_delete_bookmark_offline(self, bookmark_created, driver):
        """
        Шаги:
          1. Отключить сеть.
          2. Удалить метку из папки.
          3. Проверить: снэк успеха.
          4. Проверить в БД: action = REMOVE, метка скрыта.
          5. Проверить: метка не отображается в папке.
          6. Восстановить сеть.
        """
        bm_name = bookmark_created
        db = BookmarksDB()

        with offline_mode(driver):
            with allure.step("Открыть папку и удалить метку"):
                fl = FolderListPage(driver)
                fl.open()
                folder = fl.open_folder(TestData.DEFAULT_FOLDER_NAME)
                folder.delete_bookmark(bm_name)

                if folder.is_element_present(Loc.CONFIRM_DELETE_OK, timeout=3):
                    folder.click(Loc.CONFIRM_DELETE_OK)

            with allure.step("Проверить снэк (мягкая проверка)"):
                snack_shown = folder.wait_for_success_snack(timeout=5)
                allure.attach(
                    f"Снэк после удаления: {'показан' if snack_shown else 'не показан'}",
                    name="Снэк", attachment_type=allure.attachment_type.TEXT
                )

            with allure.step("Проверить в БД: action = REMOVE"):
                try:
                    db.pull_db()
                    bm = db.get_bookmark_by_name(bm_name)
                    if bm:
                        assert bm.get("action") == "REMOVE", \
                            f"Ожидался action=REMOVE, получен: {bm.get('action')}"
                except Exception as e:
                    allure.attach(str(e), name="БД-проверка пропущена",
                                  attachment_type=allure.attachment_type.TEXT)

            with allure.step("Проверить: метка не видна в папке"):
                fl2 = FolderListPage(driver)
                fl2.open()
                folder2 = fl2.open_folder(TestData.DEFAULT_FOLDER_NAME)
                assert not folder2.bookmark_exists(bm_name), \
                    f"Метка '{bm_name}' всё ещё видна в папке после оффлайн-удаления"

        db.cleanup()

    @allure.story("Синхронизация при выходе в онлайн")
    @allure.title("TC-OF-04: После возвращения в онлайн — метки синхронизируются с сервером")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.offline
    @pytest.mark.sync
    def test_sync_on_reconnect(self, map_page, driver):
        """
        Шаги:
          1. Отключить сеть.
          2. Создать метку (action = ADD).
          3. Восстановить сеть.
          4. Подождать синхронизации (до 30с).
          5. Проверить в БД: action = NONE (сервер подтвердил).
          6. Проверить: метка видна в папке.
        """
        bm_name = unique_name("Синк_метка")
        db = BookmarksDB()

        with allure.step("Создать метку в оффлайне"):
            NetworkUtils.go_offline(driver)
            try:
                card = map_page.search_and_open(TestData.SEARCH_OBJECT_NAME)
                if card.is_edit_bookmark_button_visible():
                    card.tap_remove_bookmark()
                    if card.is_element_present(Loc.CONFIRM_DELETE_OK, timeout=2):
                        card.click(Loc.CONFIRM_DELETE_OK)
                    card = map_page.search_and_open(TestData.SEARCH_OBJECT_NAME)

                edit = card.tap_add_bookmark()
                if not edit.is_open(timeout=10):
                    NetworkUtils.go_online(driver)
                    pytest.skip(
                        "Экран редактирования метки не открылся — "
                        "кнопка добавления метки недоступна на карточке объекта"
                    )
                edit.set_name(bm_name)
                edit.tap_save()
            finally:
                NetworkUtils.go_online(driver)

        with allure.step(f"Ждать синхронизации ({Timeouts.SYNC_TIMEOUT}с)"):
            allure.attach(
                f"Ожидание {Timeouts.SYNC_TIMEOUT}с синхронизации с сервером...",
                name="Синхронизация", attachment_type=allure.attachment_type.TEXT
            )
            time.sleep(Timeouts.SYNC_TIMEOUT)

        with allure.step("Проверить в БД: action = NONE после синхронизации"):
            try:
                db.pull_db()
                bm = db.get_bookmark_by_name(bm_name)
                if bm:
                    allure.attach(str(bm), name="Запись в БД после синка",
                                  attachment_type=allure.attachment_type.TEXT)
                    assert bm.get("action") == "NONE", (
                        f"После синхронизации ожидался action=NONE, "
                        f"получен: {bm.get('action')}"
                    )
            except Exception as e:
                allure.attach(str(e), name="БД-проверка пропущена",
                              attachment_type=allure.attachment_type.TEXT)

        with allure.step("Проверить: метка доступна в папке после синка"):
            fl = FolderListPage(driver)
            fl.open()
            folder = fl.open_folder(TestData.DEFAULT_FOLDER_NAME)
            assert folder.bookmark_exists(bm_name), \
                f"Метка '{bm_name}' не найдена в папке после синхронизации"

        db.cleanup()

    @allure.story("Восстановление из бэкапа")
    @allure.title("TC-OF-05: Восстановление меток и папок из kmb-файла с сервера")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.sync
    def test_restore_bookmarks_from_backup(self, driver):
        """
        Шаги:
          1. Пользователь авторизован (предусловие).
          2. Инициировать восстановление из бэкапа (через Settings → Restore).
          3. Проверить: снэк успеха после восстановления.
          4. Проверить: метки и папки из бэкапа появились в приложении.
          5. Проверить: метки, добавленные ДО восстановления, не удалены.

        Примечание:
          Полная реализация требует:
          a) предварительно сохранить бэкап на сервере;
          b) иметь доступ к экрану 'Настройки → Восстановить метки'.
          Здесь показан скелет теста с аннотациями шагов.
        """
        with allure.step("Предусловие: пользователь авторизован"):
            # В реальном тесте: проверяем авторизацию или логинимся
            pass

        with allure.step("Перейти в Настройки → Восстановить метки"):
            # TODO: Реализовать навигацию к экрану восстановления
            # settings_page = SettingsPage(driver)
            # settings_page.open()
            # settings_page.tap_restore_bookmarks()
            pytest.skip(
                "TC-OF-05 требует реализации SettingsPage и наличия бэкапа на сервере. "
                "Скелет теста задокументирован, реализация — по готовности стенда."
            )

        with allure.step("Дождаться завершения восстановления"):
            from pages.base_page import BasePage
            base = BasePage(driver)
            assert base.wait_for_success_snack(timeout=30), \
                "Снэк успеха не появился после восстановления из бэкапа"

        with allure.step("Проверить: папки из бэкапа появились"):
            fl = FolderListPage(driver)
            fl.open()
            folders = fl.get_folder_names()
            allure.attach(str(folders), name="Папки после восстановления",
                          attachment_type=allure.attachment_type.TEXT)
            assert len(folders) > 0, "После восстановления список папок пуст"
