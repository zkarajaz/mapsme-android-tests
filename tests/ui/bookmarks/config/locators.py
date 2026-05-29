"""
config/locators.py
==================
Locators for MAPS.ME application.

APP STRUCTURE:
  Map → tap on object → Collapsed card → swipe up → Full card
  Full card → flag (place_bookmark_button) → Edit bookmark
  Full card (after adding bookmark) → My Places line → pencil → Edit bookmark
  Tabbar → Favorites → Folder screen (My Places)
  Favorites → tap on "My Places" → Screen with bookmarks inside folder
"""
from appium.webdriver.common.appiumby import AppiumBy


class Loc:

    # Tabbar - bottom navigation

    # Вкладка Поиск (Search) — bounds=[0,2214][216,2361]  центр (108, 2287)
    TAB_SEARCH = (AppiumBy.XPATH,
        "//*[@resource-id='bottom_bar_search']")

    # Вкладка Маршруты (Route) — bounds=[216,2214][432,2361]  центр (324, 2287)
    TAB_ROUTES = (AppiumBy.XPATH,
        "//*[@resource-id='bottom_bar_routes']")

    # Вкладка Хаб (Hub) — bounds=[432,2214][648,2361]  центр (540, 2287)
    TAB_HUB = (AppiumBy.XPATH,
        "//*[@resource-id='bottom_bar_hub']")

    # Вкладка Избранное (Favorites) — bounds=[648,2214][864,2361]  центр (756, 2287)
    TAB_BOOKMARKS = (AppiumBy.XPATH,
        "//*[@resource-id='bottom_bar_favorites']")

    # Вкладка Ещё (More) — bounds=[864,2214][1080,2361]  центр (972, 2287)
    TAB_MORE = (AppiumBy.XPATH,
        "//*[@resource-id='bottom_bar_more']")

    # Координаты таббара для tap_coords() — используются как fallback
    TAB_SEARCH_COORDS    = (108, 2287)
    TAB_ROUTES_COORDS    = (324, 2287)
    TAB_HUB_COORDS       = (540, 2287)
    TAB_BOOKMARKS_COORDS = (756, 2287)
    TAB_MORE_COORDS      = (972, 2287)

    # Object card (bottom sheet after map tap)

    # Кнопка флажка "Добавить/удалить избранное" — resource-id='place_bookmark_button'
    # bounds=[729,2213][873,2340]  видна ТОЛЬКО в свёрнутой карточке
    CARD_BOOKMARK_BTN = (AppiumBy.XPATH,
        "//*[@resource-id='place_bookmark_button']")

    # Координаты кнопки флажка (fallback если xpath не работает)
    CARD_BOOKMARK_COORDS = (801, 2276)

    # Заголовок карточки объекта — первый крупный TextView
    CARD_TITLE = (AppiumBy.XPATH,
        "(//android.widget.TextView)[1]")

    # Содержит название папки и кнопку-карандаш для редактирования
    CARD_MY_PLACES_TEXT = (AppiumBy.XPATH,
        "//*[contains(@text,'My Places')]")

    # Кнопка-карандаш Edit рядом с "My Places" — View после текста My Places
    CARD_EDIT_PENCIL = (AppiumBy.XPATH,
        "//*[contains(@text,'My Places')]"
        "/following-sibling::android.view.View[@clickable='true']")

    # Координата карандаша (правый край строки My Places ~446, 163)
    CARD_EDIT_PENCIL_COORDS = (446, 163)

    # Edit bookmark screen

    # Заголовок экрана редактирования метки
    EDIT_BM_TITLE = (AppiumBy.XPATH,
        "//*[contains(@text,'Edit bookmark') or contains(@text,'Add bookmark')]")

    # Поле имени метки — EditText с ресурсом edit_bookmark_name_text_field
    EDIT_BM_NAME = (AppiumBy.XPATH,
        "//*[@resource-id='edit_bookmark_name_text_field']")

    # Поле описания метки — EditText с ресурсом edit_bookmark_description_text_field
    EDIT_BM_DESC = (AppiumBy.XPATH,
        "//*[@resource-id='edit_bookmark_description_text_field']")

    # Кнопка "Save" (синяя полная кнопка снизу) — ресурс edit_bookmark_apply_button
    EDIT_BM_SAVE = (AppiumBy.XPATH,
        "//*[@resource-id='edit_bookmark_apply_button']")

    # Кнопка смены цвета — верхняя часть экрана, ресурс edit_color_card
    EDIT_BM_COLOR_BTN = (AppiumBy.XPATH,
        "//*[@resource-id='edit_color_card']")

    # Кнопка удаления метки (иконка мусорки) — правый верхний угол экрана
    EDIT_BM_DELETE = (AppiumBy.XPATH,
        "//*[@resource-id='edit_bookmark_delete_button'] "
        "| //*[contains(@content-desc,'delete') or contains(@content-desc,'trash')]"
        "[@clickable='true']")

    # Координаты мусорки — правый верхний угол
    EDIT_BM_DELETE_COORDS = (470, 75)

    # Кнопка Назад в тулбаре Edit bookmark
    EDIT_BM_BACK = (AppiumBy.XPATH,
        "//android.widget.ImageButton[@content-desc='Navigate up' "
        "or @content-desc='Back' or @content-desc='Назад' "
        "or @content-desc='Go back']")

    # Строка выбора папки (My Places → ) — кликабельная
    # Координата центра этой строки: x=278, y=1401
    EDIT_BM_FOLDER_ROW_COORDS = (278, 1401)

    # Счётчик символов "14 / 60" под полем имени
    CHAR_COUNTER_60 = (AppiumBy.XPATH,
        "//*[contains(@text,'/ 60') or contains(@text,'/60')]")

    # Favorites screen - main screen (shows list of folders)

    # Корневой контейнер главного экрана Favorites
    FAV_CONTAINER = (AppiumBy.XPATH,
        "//*[@resource-id='favorites_container']")

    # Корневой контейнер экрана внутри папки (My Places / custom)
    FOLDER_CONTAINER = (AppiumBy.XPATH,
        "//*[@resource-id='bookmarks_container']")

    # Кнопка Назад внутри папки (bookmarks screen)
    FAV_BACK = (AppiumBy.XPATH,
        "//*[@resource-id='bookmarks_back_button']")

    # Кнопка меню "..." (три точки) → "Add folder", "Import"  (ГЛАВНЫЙ экран Favorites)
    FAV_MENU = (AppiumBy.XPATH,
        "//*[@resource-id='favorites_menu_button']")

    # ALIAS для совместимости
    FAVORITES_MENU = (AppiumBy.XPATH,
        "//*[@resource-id='favorites_menu_button']")

    # Заголовок внутри папки (bookmarks_title_text = название папки, напр. "My Places")
    FAV_TITLE = (AppiumBy.XPATH,
        "//*[@resource-id='bookmarks_title_text']")

    # Поле поиска (лупа сверху) в экране избранного
    # Search field - search icon with microphone
    FAV_SEARCH_ICON = (AppiumBy.XPATH,
        "//*[@content-desc='search icon' or @resource-id='bookmarks_search_view']")

    # EditText внутри строки поиска после нажатия на иконку
    FAV_SEARCH_INPUT = (AppiumBy.XPATH,
        "//android.widget.EditText[1]")

    # Глобальный переключатель "Show all bookmarks on map"
    # Global toggle "Show all bookmarks on map" - blue toggle at bottom
    FAV_ALL_SWITCH = (AppiumBy.XPATH,
        "//*[@resource-id='favorites_show_all_categories_switch']")

    # Folder "My Places" in main favorites screen

    # Строка папки "My Places" — кликабельный View с текстом "My Places"
    # "My Places" folder row - gray card with folder icon and text
    FOLDER_MY_PLACES_ROW = (AppiumBy.XPATH,
        "//android.view.View[@clickable='true'][.//android.widget.TextView"
        "[contains(@text,'My Places')]]")

    # Folder content screen (after entering "My Places")

    # Кнопка меню "..." внутри папки → Edit folder, Group by, Share...
    # Menu button inside folder - three dots in right upper corner inside folder
    FOLDER_CONTENT_MENU = (AppiumBy.XPATH,
        "//*[@resource-id='bookmarks_menu_button']")

    # Ячейка метки внутри папки — кликабельный View с TextViews
    # Bookmark cell in folder - row contains type, name, address, distance
    BOOKMARK_IN_FOLDER_CELL = (AppiumBy.XPATH,
        "//android.view.View[@clickable='true']"
        "[.//android.widget.TextView[contains(@text,'bookmark')]]")

    # Первый TextView в ячейке метки = тип ("bookmark")
    BM_CELL_TYPE = (AppiumBy.XPATH, "(.//android.widget.TextView)[1]")

    # Второй TextView = НАЗВАНИЕ метки (реальное имя, которое мы ищем)
    BM_CELL_NAME = (AppiumBy.XPATH, "(.//android.widget.TextView)[2]")

    # Третий TextView = адрес
    BM_CELL_ADDR = (AppiumBy.XPATH, "(.//android.widget.TextView)[3]")

    # Четвёртый TextView = расстояние (опционально)
    BM_CELL_DIST = (AppiumBy.XPATH, "(.//android.widget.TextView)[4]")

    # Кнопка "..." у метки — динамический resource-id: bookmark_card_more_button_{NAME}
    BM_MORE_BTN = (AppiumBy.XPATH,
        "//*[contains(@resource-id,'bookmark_card_more_button')][@clickable='true']")

    # Menu in main favorites screen

    # Пункт "Add folder" в меню (без [@clickable] — в Compose меню текст может быть некликабелен)
    MENU_ADD_FOLDER = (AppiumBy.XPATH,
        "//*[contains(@text,'Add folder') or contains(@text,'New list') "
        "or contains(@text,'Add list') or contains(@text,'New folder')]")

    # Пункт "Import" в меню
    MENU_IMPORT = (AppiumBy.XPATH,
        "//*[contains(@text,'Import')]")

    # Menu in folder

    # Пункт "Edit folder" — открывает экран редактирования папки
    MENU_EDIT_FOLDER = (AppiumBy.XPATH,
        "//*[contains(@text,'Edit folder')]")

    # Пункты сортировки "Group by: Distance, Date, Name, None" (Type отсутствует в приложении)
    MENU_SORT_DISTANCE = (AppiumBy.XPATH, "//*[@text='Distance'][@clickable='true']")
    MENU_SORT_DATE     = (AppiumBy.XPATH, "//*[@text='Date'][@clickable='true']")
    MENU_SORT_NAME     = (AppiumBy.XPATH, "//*[@text='Name'][@clickable='true']")

    # Add/Edit folder screen

    # Заголовок экрана добавления/редактирования папки
    FOLDER_SCREEN_TITLE = (AppiumBy.XPATH,
        "//*[contains(@text,'Add folder') or contains(@text,'Edit folder')]")

    # Поле "Name" (название папки) — resource-id favorites_add_name_text_field
    FOLDER_NAME_INPUT = (AppiumBy.XPATH,
        "//*[@resource-id='favorites_add_name_text_field']")

    # Поле "Description" (описание папки)
    FOLDER_DESC_INPUT = (AppiumBy.XPATH,
        "(//android.widget.EditText)[2]")

    # Add folder button or Save button - at bottom of screen
    # NOTE: keep [@clickable='true'] to avoid matching the screen title "Add folder"
    FOLDER_SAVE_BTN = (AppiumBy.XPATH,
        "//*[@text='Add folder' or @text='Save' or @text='Create'][@clickable='true']")

    # Кнопка удаления папки (мусорка) — если доступна
    FOLDER_DELETE_BTN = (AppiumBy.XPATH,
        "//*[@content-desc='icon trash' or contains(@resource-id,'delete')]")

    # Confirmation dialog (standard Android AlertDialog)

    # Кнопка подтверждения (Delete/OK/Yes)
    DIALOG_OK = (AppiumBy.XPATH, "//*[@text='Delete']")

    # Кнопка отмены (Cancel/No)
    DIALOG_CANCEL = (AppiumBy.XPATH, "//*[@text='Cancel']")

    # Notifications (snacks)

    # Снэк успеха — появляется после save/delete
    SNACK_SUCCESS = (AppiumBy.XPATH,
        "//*[contains(@text,'saved') or contains(@text,'Saved') "
        "or contains(@text,'Added') or contains(@text,'Deleted')]"
        "[not(@resource-id='bookmarks_title_text')]")

    # Снэк ошибки
    SNACK_ERROR = (AppiumBy.XPATH,
        "//*[contains(@text,'Error') or contains(@text,'already exists')]")

    # Aliases used in tests
    CONFIRM_DELETE_OK     = (AppiumBy.XPATH, "//*[@text='Delete']")
    CONFIRM_DELETE_CANCEL = (AppiumBy.XPATH, "//*[@text='Cancel']")
    CARD_OBJECT_TITLE     = (AppiumBy.XPATH, "(//android.widget.TextView)[1]")

    # Color cells in color picker (Edit bookmark screen)
    EDIT_BM_COLOR_CELL = (AppiumBy.XPATH,
        "//*[contains(@resource-id,'color_cell') "
        "or contains(@resource-id,'edit_color')][@clickable='true']")

    # Eye icon inside a folder row (visibility toggle)
    FOLDER_EYE_BTN = (AppiumBy.XPATH,
        "//*[contains(@resource-id,'eye') "
        "or contains(@content-desc,'eye')][@clickable='true']")

    # Folder row (generic — any clickable row with "bookmarks" text)
    FOLDER_ROW = (AppiumBy.XPATH,
        "//android.view.View[@clickable='true']"
        "[.//android.widget.TextView[contains(@text,'bookmark')]]")
