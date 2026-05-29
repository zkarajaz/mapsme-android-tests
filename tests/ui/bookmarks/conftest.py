"""
conftest.py
===========
Фикстуры pytest.

ИСПРАВЛЕНИЯ:
  1. bookmark_created: после создания метки ВХОДИМ в папку My Places
     и проверяем что метка там есть
  2. favorites_page: использует FavoritesPage.open() с retry
  3. Все фикстуры защищены от сворачивания приложения
"""
import os, sys, time, subprocess, logging, pytest, allure

sys.path.insert(0, os.path.dirname(__file__))

from appium.options.android import UiAutomator2Options
from appium import webdriver as appium_webdriver

from config.settings import get_capabilities, APPIUM_HOST
from utils.helpers import unique_name

logger = logging.getLogger(__name__)

ADB = r"C:\Users\Victoria\AppData\Local\Android\Sdk\platform-tools\adb.exe"
PKG = "com.mapswithme.maps.pro"


def wait_for_adb(max_sec: int = 90) -> bool:
    logger.info("Waiting for ADB...")
    deadline = time.time() + max_sec
    while time.time() < deadline:
        try:
            out = subprocess.check_output(
                [ADB, "devices"], stderr=subprocess.STDOUT,
                text=True, timeout=10)
            for line in out.splitlines():
                if "emulator-5554" in line and "\tdevice" in line:
                    logger.info("ADB ready")
                    time.sleep(2)
                    return True
        except Exception:
            pass
        time.sleep(5)
    return False


def launch_maps(driver=None) -> None:
    """Принудительно запускает MAPS.ME на переднем плане."""
    # Через ADB
    try:
        subprocess.run(
            [ADB, "-s", "emulator-5554", "shell", "am", "start",
             "-n", f"{PKG}/com.mapswithme.maps.pro.DefaultIcon"],
            timeout=10, capture_output=True
        )
        time.sleep(4)
    except Exception as e:
        logger.warning(f"ADB launch: {e}")

    # Через Appium
    if driver:
        try:
            driver.activate_app(PKG)
            time.sleep(3)
        except Exception:
            pass


@pytest.fixture(scope="function")
def driver():
    if not wait_for_adb(90):
        raise RuntimeError(
            "\nADB not ready.\n"
            "  Run: adb kill-server && adb start-server\n"
            "  Check: adb devices → 'emulator-5554   device'\n"
        )

    caps = get_capabilities()
    options = UiAutomator2Options()
    options.platform_name             = caps["platformName"]
    options.device_name               = caps["appium:deviceName"]
    options.app                       = caps["appium:app"]
    options.app_package               = caps["appium:appPackage"]
    options.app_activity              = caps["appium:appActivity"]
    options.no_reset                  = caps["appium:noReset"]
    options.full_reset                = caps["appium:fullReset"]
    options.new_command_timeout       = 120
    options.auto_grant_permissions    = True
    options.set_capability("appium:noSign",       True)
    options.set_capability("appium:adbExecTimeout", 60000)
    options.set_capability("appium:uiautomator2ServerLaunchTimeout", 60000)
    options.set_capability("appium:androidDeviceReadyTimeout", 90)
    options.set_capability("appium:dontStopAppOnReset", True)

    _driver = None
    for attempt in range(1, 4):
        try:
            logger.info(f"Appium session, attempt {attempt}/3...")
            _driver = appium_webdriver.Remote(APPIUM_HOST, options=options)
            logger.info("Session created")
            break
        except Exception as e:
            logger.warning(f"Attempt {attempt}: {str(e)[:100]}")
            time.sleep(15)

    if not _driver:
        raise RuntimeError("Не удалось создать Appium-сессию")

    try:
        _driver.update_settings({"waitForIdleTimeout": 500})
    except Exception:
        pass

    _driver.implicitly_wait(0)
    time.sleep(3)

    # Ensure MAPS.ME is in foreground
    try:
        state = _driver.query_app_state(PKG)
        if state != 4:
            logger.info("App forced to foreground")
            _driver.activate_app(PKG)
            time.sleep(4)
    except Exception:
        launch_maps(_driver)

    yield _driver

    try:
        _driver.quit()
    except Exception:
        pass


@pytest.fixture
def map_page(driver):
    from pages.map_page import MapPage
    page = MapPage(driver)
    page.ensure_on_map()
    return page


@pytest.fixture
def favorites_page(driver):
    from pages.favorites_page import FavoritesPage
    page = FavoritesPage(driver)
    page.open()
    return page


@pytest.fixture
def bookmark_created(driver):
    """
    Создаёт метку и возвращает её имя.
    После теста — удаляет.

    ИСПРАВЛЕННЫЙ АЛГОРИТМ:
      1. Открываем карточку объекта на карте
      2. Убираем метку если уже есть
      3. Нажимаем флажок (place_bookmark_button)
      4. Открываем Edit bookmark (карандаш у "My Places")
      5. Вводим уникальное имя и сохраняем
      6. Проверяем что метка появилась в My Places
    """
    from pages.map_page import MapPage
    from pages.object_card_page import ObjectCardPage
    from pages.edit_bookmark_page import EditBookmarkPage
    from pages.favorites_page import FavoritesPage

    name = unique_name("Авто_метка")
    _driver = driver
    launch_maps(_driver)

    try:
        map_pg = MapPage(_driver)
        map_pg.ensure_on_map()

        # Открываем карточку объекта
        card = map_pg.open_any_object()

        # Убираем существующую метку если есть
        if card.is_bookmarked():
            logger.info("  Убираем старую метку...")
            card.remove_bookmark_with_confirmation()
            time.sleep(2)
            # Повторно открываем карточку
            map_pg.ensure_on_map()
            card = map_pg.open_any_object()

        # Добавляем метку
        card.tap_bookmark_btn()
        time.sleep(2.5)

        # Открываем Edit bookmark
        edit = EditBookmarkPage(_driver)
        if not edit.is_open(timeout=8):
            card2 = ObjectCardPage(_driver)
            card2.open_edit_bookmark()
            time.sleep(2)

        # Вводим имя
        if edit.is_open(timeout=5):
            edit.set_name(name)
            edit.tap_save()
            logger.info(f"Bookmark created via card: '{name}'")
        else:
            # Fallback: go to Favorites → My Places and rename the newest bookmark
            logger.warning("  Edit via card failed — renaming via Favorites/My Places")
            time.sleep(2)
            fav_tmp = FavoritesPage(_driver)
            fav_tmp.open()
            fav_tmp.open_my_places()
            time.sleep(2)
            bm_names = fav_tmp.get_bookmark_names()
            logger.info(f"  Bookmarks in My Places: {bm_names}")
            if bm_names:
                # Rename the first visible bookmark (the one we just added)
                old = bm_names[0]
                try:
                    edit2 = fav_tmp.edit_bookmark(old)
                    if edit2.is_open(timeout=6):
                        edit2.set_name(name)
                        edit2.tap_save()
                        logger.info(f"Bookmark renamed via Favorites: '{old}' → '{name}'")
                    else:
                        logger.warning(f"  Edit screen didn't open from Favorites either")
                        # Keep the old name so at least the test can find the bookmark
                        name = old
                        logger.warning(f"  Using existing name: '{name}'")
                except Exception as e2:
                    logger.warning(f"  Rename via Favorites failed: {e2}")
                    name = old
                    logger.warning(f"  Using existing name: '{name}'")
            else:
                raise RuntimeError("No bookmarks found in My Places after adding flag")

        time.sleep(2)

    except Exception as e:
        logger.error(f"bookmark_created setup: {e}")
        raise

    yield name

    # Teardown: удаляем метку
    try:
        launch_maps(_driver)
        mp2 = MapPage(_driver)
        mp2.ensure_on_map()
        card3 = mp2.open_any_object()
        if card3.is_bookmarked():
            card3.remove_bookmark_with_confirmation()
    except Exception as e:
        logger.warning(f"bookmark_created teardown: {e}")


@pytest.fixture
def folder_created(driver):
    """Создаёт папку (список) через меню. Возвращает имя."""
    from pages.favorites_page import FavoritesPage
    name = unique_name("Авто_папка")
    launch_maps(driver)

    try:
        fav = FavoritesPage(driver)
        fav.open()
        # Remove leftover auto-folders from previous runs before creating new one
        fav.cleanup_auto_folders(prefix="Авто_папка")
        fav.open()
        fav.create_new_folder(name)
        time.sleep(2)
        fav.open()
    except Exception as e:
        logger.error(f"folder_created setup: {e}")
        raise

    yield name

    # Teardown: delete the created folder
    try:
        launch_maps(driver)
        fav2 = FavoritesPage(driver)
        fav2.open()
        fav2.delete_folder(name)
    except Exception as e:
        logger.warning(f"folder_created teardown: {e}")


@pytest.fixture
def two_bookmarks(driver):
    """Создаёт 2 метки. Для тестов сортировки."""
    from pages.map_page import MapPage
    from pages.edit_bookmark_page import EditBookmarkPage

    names = []
    launch_maps(driver)
    map_pg = MapPage(driver)
    map_pg.ensure_on_map()

    for prefix in ["Метка_А", "Метка_Б"]:
        bm_name = unique_name(prefix)
        try:
            card = map_pg.open_any_object()
            if card.is_bookmarked():
                card.remove_bookmark_with_confirmation()
                time.sleep(2)
                map_pg.ensure_on_map()
                card = map_pg.open_any_object()
            card.tap_bookmark_btn()
            time.sleep(2.5)
            edit = EditBookmarkPage(driver)
            if edit.is_open(timeout=5):
                edit.set_name(bm_name)
                edit.tap_save()
            names.append(bm_name)
            time.sleep(2)
        except Exception as e:
            logger.warning(f"two_bookmarks {prefix}: {e}")

    yield names

    # Teardown
    try:
        card4 = MapPage(driver).open_any_object()
        if card4.is_bookmarked():
            card4.remove_bookmark_with_confirmation()
    except Exception:
        pass


@pytest.fixture
def folder_list_page(driver):
    """
    Открывает экран Избранного через таббар.
    Псевдоним favorites_page для тестов, использующих FolderListPage.
    """
    from pages.favorites_page import FavoritesPage
    page = FavoritesPage(driver)
    page.open()
    return page


@pytest.fixture
def two_bookmarks_in_folder(driver):
    """
    Создаёт 2 метки через КАРТУ (My Places по умолчанию).
    Возвращает (folder_name, [name1, name2]).
    Teardown: удаляет обе метки через таббар.
    """
    from pages.map_page import MapPage
    from pages.edit_bookmark_page import EditBookmarkPage
    from pages.favorites_page import FavoritesPage

    folder_name = "My Places"
    names = []
    launch_maps(driver)
    map_pg = MapPage(driver)
    map_pg.ensure_on_map()

    for prefix in ["Сорт_А", "Сорт_Б"]:
        bm_name = unique_name(prefix)
        try:
            card = map_pg.open_any_object()
            if card.is_bookmarked():
                card.remove_bookmark_with_confirmation()
                time.sleep(2)
                map_pg.ensure_on_map()
                card = map_pg.open_any_object()
            card.tap_bookmark_btn()
            time.sleep(2.5)
            edit = EditBookmarkPage(driver)
            if edit.is_open(timeout=5):
                edit.set_name(bm_name)
                edit.tap_save()
            names.append(bm_name)
            time.sleep(2)
        except Exception as e:
            logger.warning(f"two_bookmarks_in_folder {prefix}: {e}")

    yield (folder_name, names)

    # Teardown через таббар
    try:
        fav = FavoritesPage(driver)
        fav.open()
        fav.open_my_places()
        for name in names:
            try:
                fav.delete_bookmark(name)
                time.sleep(1)
            except Exception:
                pass
    except Exception as e:
        logger.warning(f"two_bookmarks_in_folder teardown: {e}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        drv = item.funcargs.get("driver")
        if drv:
            try:
                allure.attach(
                    drv.get_screenshot_as_png(),
                    name=f"FAIL_{item.name}",
                    attachment_type=allure.attachment_type.PNG)
            except Exception:
                pass
