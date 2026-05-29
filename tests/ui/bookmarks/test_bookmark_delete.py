import pytest
import allure

from config.settings import TestData
from config.locators import Loc
from pages.map_page import MapPage
from pages.folder_list_page import FolderListPage
from pages.object_card_page import ObjectCardPage
from utils.helpers import unique_name

@allure.epic("Метки (Bookmarks)")
@allure.feature("Удаление меток")
class TestBookmarkDelete:

    @allure.story("Удаление из карточки объекта")
    @allure.title("TC-DEL-01: Удаление метки через кнопку в карточке объекта")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.delete
    def test_delete_from_object_card(self, map_page, bookmark_created, driver):
        """
        Шаги:
          1. Открыть карточку объекта (метка уже добавлена).
          2. Нажать 'Удалить из избранного'.
          3. Подтвердить удаление в диалоге (если есть).
          4. Проверить: кнопка сменилась на 'Добавить в избранное'.
          5. Проверить: снэк успеха.
        """
        with allure.step("Открыть карточку объекта"):
            # bookmark_created оставляет карточку открытой после tap_save()
            # используем её напрямую, не открывая новую
            card = ObjectCardPage(driver)
            if not card.is_bookmarked():
                map_page.ensure_on_map()
                card = map_page.open_any_object()
            assert card.is_edit_bookmark_button_visible(), \
                "Кнопка редактирования не найдена — объект должен быть в избранном"

        with allure.step("Удалить метку"):
            card.tap_remove_bookmark()

        with allure.step("Подтвердить удаление (если появился диалог)"):
            if card.is_element_present(Loc.CONFIRM_DELETE_OK, timeout=3):
                card.click(Loc.CONFIRM_DELETE_OK)

        with allure.step("Проверить: кнопка 'Добавить в избранное' вернулась"):
            assert card.is_add_bookmark_button_visible(), \
                "После удаления не появилась кнопка 'Добавить в избранное'"

        with allure.step("Проверить снэк успеха (опционально)"):
            snack = card.wait_for_success_snack()
            allure.attach(
                f"Снэк успеха: {'появился' if snack else 'не появился (нормально для toggle-удаления)'}",
                name="Снэк", attachment_type=allure.attachment_type.TEXT
            )

    @allure.story("Удаление из открытой папки")
    @allure.title("TC-DEL-02: Удаление метки свайпом в открытой папке")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.delete
    def test_delete_from_folder_swipe(self, bookmark_created, driver):
        """
        Шаги:
          1. Открыть папку с меткой.
          2. Свайп влево по метке → нажать кнопку удаления.
          3. Подтвердить.
          4. Проверить: метка исчезла из папки.
        """
        bm_name = bookmark_created

        with allure.step("Открыть папку"):
            fl = FolderListPage(driver)
            fl.open()
            folder = fl.open_folder(TestData.DEFAULT_FOLDER_NAME)
            assert folder.bookmark_exists(bm_name), \
                f"Метка '{bm_name}' не найдена в папке перед удалением"

        with allure.step("Удалить метку свайпом"):
            folder.delete_bookmark(bm_name)

        with allure.step("Подтвердить удаление (если диалог)"):
            if folder.is_element_present(Loc.CONFIRM_DELETE_OK, timeout=3):
                folder.click(Loc.CONFIRM_DELETE_OK)

        with allure.step("Проверить: метка исчезла из папки"):
            assert not folder.bookmark_exists(bm_name), \
                f"Метка '{bm_name}' всё ещё присутствует в папке после удаления"

    @allure.story("Удаление из режима редактирования")
    @allure.title("TC-DEL-03: Удаление метки через кнопку в экране редактирования")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.delete
    def test_delete_from_edit_screen(self, bookmark_created, driver):
        """
        Шаги:
          1. Открыть папку → нажать на метку → открыть редактирование.
          2. Нажать кнопку 'Удалить' на экране редактирования.
          3. Подтвердить.
          4. Проверить: метка исчезла из папки.
        """
        bm_name = bookmark_created

        with allure.step("Открыть папку → редактирование метки"):
            fl = FolderListPage(driver)
            fl.open()
            folder = fl.open_folder(TestData.DEFAULT_FOLDER_NAME)
            edit = folder.edit_bookmark(bm_name)

        with allure.step("Нажать 'Удалить' в редакторе"):
            edit.tap_delete()

        with allure.step("Подтвердить удаление"):
            if edit.is_element_present(Loc.CONFIRM_DELETE_OK, timeout=3):
                edit.click(Loc.CONFIRM_DELETE_OK)
            edit.wait_for_animation()

        with allure.step("Проверить: метка исчезла"):
            fl2 = FolderListPage(driver)
            fl2.open()
            folder2 = fl2.open_folder(TestData.DEFAULT_FOLDER_NAME)
            assert not folder2.bookmark_exists(bm_name), \
                f"Метка '{bm_name}' не была удалена"

    @allure.story("Диалог подтверждения")
    @allure.title("TC-DEL-04: Отмена удаления — метка остаётся")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.delete
    def test_cancel_delete_keeps_bookmark(self, bookmark_created, driver):
        """
        Шаги:
          1. Открыть редактирование метки → нажать 'Удалить'.
          2. В диалоге нажать 'Отмена'.
          3. Проверить: метка всё ещё существует в папке.
        """
        bm_name = bookmark_created

        with allure.step("Открыть редактирование и нажать 'Удалить'"):
            fl = FolderListPage(driver)
            fl.open()
            folder = fl.open_folder(TestData.DEFAULT_FOLDER_NAME)
            edit = folder.edit_bookmark(bm_name)
            edit.tap_delete()

        with allure.step("Нажать 'Отмена' в диалоге"):
            if edit.is_element_present(Loc.CONFIRM_DELETE_CANCEL, timeout=3):
                edit.click(Loc.CONFIRM_DELETE_CANCEL)
            else:
                pytest.skip("Диалог подтверждения не появился — возможно, удаление без диалога")

        with allure.step("Проверить: метка не удалена"):
            # Нажимаем Назад, чтобы вернуться в папку
            edit.tap_back()
            fl2 = FolderListPage(driver)
            fl2.open()
            folder2 = fl2.open_folder(TestData.DEFAULT_FOLDER_NAME)
            assert folder2.bookmark_exists(bm_name), \
                f"Метка '{bm_name}' была удалена, хотя пользователь нажал 'Отмена'"
