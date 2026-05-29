# MAPS.ME Android Automated Tests

Автоматизированный тест-сьют для проверки API и мобильного UI сервиса подписок MAPS.ME PRO.

---

## Структура проекта

```
msps_tests/
├── api/                        # HTTP-клиенты для работы с API
├── config/
│   ├── settings.py             # Конфиг: BASE_URL, JWT-токен, эндпоинты
│   └── endpoints.py
├── tests/
│   ├── api/                    # API-тесты (7 модулей, 54 теста)
│   │   ├── test_user_details.py
│   │   ├── test_email.py
│   │   ├── test_user_agreement.py
│   │   ├── test_subscription_plans.py
│   │   ├── test_payment_methods.py
│   │   ├── test_subscriptions.py
│   │   └── test_payment.py
│   └── ui/                     # UI-тесты на Appium
│       ├── test_ui.py          # Тесты подписок (6 тестов)
│       └── bookmarks/          # Тесты меток и папок (7 модулей, 30+ тестов)
│           ├── test_bookmark_creation.py
│           ├── test_bookmark_edit.py
│           ├── test_bookmark_delete.py
│           ├── test_folder_management.py
│           ├── test_map_display.py
│           ├── test_search_sort.py
│           ├── test_offline_sync.py
│           ├── pages/          # Page Object Model
│           ├── config/         # Локаторы и настройки
│           └── utils/          # Вспомогательные утилиты
├── utils/
│   ├── helpers.py
│   └── schemas/                # JSON Schema для валидации ответов
├── conftest.py                 # Фикстуры pytest (auth_client, driver и др.)
├── pytest.ini
└── requirements.txt
```

---

## Требования

- Python 3.10+
- Android-эмулятор `emulator-5554` (для UI-тестов)
- Appium Server 2.x (для UI-тестов)
- Приложение **MAPS.ME PRO** установлено на эмуляторе с авторизованным аккаунтом, у которого есть подписка со статусом `INITIATED`

---

## Установка

```bash
# Клонировать репозиторий
git clone https://github.com/zkarajaz/mapsme-android-tests.git
cd mapsme-android-tests

# Создать и активировать виртуальное окружение
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Установить зависимости
pip install -r requirements.txt
```

---

## Настройка окружения

Создай файл `.env` в корне проекта:

```env
BASE_URL=https://api.maps.me
TEST_USER_JWT=<JWT-токен тестового пользователя>
```

> JWT-токен должен принадлежать аккаунту с INITIATED-подпиской для корректной работы UI-тестов.

---

## Запуск тестов

### Все тесты

```bash
pytest
```

### Только API-тесты

```bash
pytest tests/api/
```

### Только UI-тесты

```bash
pytest tests/ui/
```

### Конкретный модуль

```bash
pytest tests/api/test_subscriptions.py -v
```

### С HTML-отчётом

```bash
pytest --html=reports/report.html
```

---

## Allure-отчёт

```bash
# Запустить тесты (результаты сохраняются в allure-results/)
pytest

# Открыть интерактивный отчёт
allure serve allure-results
```

Для установки Allure: https://allurereport.org/docs/install/

---

## Запуск UI-тестов

UI-тесты используют Appium + UiAutomator2 для автоматизации Android-приложения.

### Предварительные условия

1. Запусти Android-эмулятор (`emulator-5554`)
2. Установи и открой MAPS.ME PRO, авторизуйся в аккаунте
3. Убедись, что аккаунт имеет подписку со статусом `INITIATED` и активным экраном подписок
4. Запусти Appium Server:

```bash
appium
```

5. Запусти тесты:

```bash
pytest tests/ui/test_ui.py -v
```

### Параметры подключения (conftest.py)

| Параметр | Значение |
|---|---|
| Appium URL | `http://127.0.0.1:4723` |
| Platform | Android |
| Device | `emulator-5554` |
| App package | `com.mapswithme.maps.pro` |
| Automation | UiAutomator2 |

---

---

## Тесты меток и папок (tests/ui/bookmarks/)

Отдельный модуль для тестирования функционала меток (bookmarks) и папок в приложении MAPS.ME.
Использует реальное Android-устройство подключённое по USB.

### Что покрыто

| Файл | Область | Тестов |
|---|---|---|
| `test_bookmark_creation.py` | Создание меток на карте | 5 |
| `test_bookmark_edit.py` | Редактирование названия, описания, цвета | 5 |
| `test_bookmark_delete.py` | Удаление меток и папок | 4 |
| `test_folder_management.py` | Создание / переименование / удаление папок | 6 |
| `test_map_display.py` | Видимость меток на карте, глобальный свитчер | 5 |
| `test_search_sort.py` | Поиск меток, сортировка по имени / дате / расстоянию | 7 |
| `test_offline_sync.py` | Создание и редактирование меток без сети | 5 |

### Требования

- Python 3.10+
- Appium Server 2.x + драйвер UiAutomator2
- Реальное Android-устройство с включённой USB-отладкой
- Приложение MAPS.ME установлено и запущено
- ADB доступен в PATH

### Установка зависимостей

```bash
pip install appium-python-client selenium pytest allure-pytest Faker
```

```bash
npm install -g appium
appium driver install uiautomator2
```

### Настройка устройства

Подключи устройство по USB и проверь подключение:

```bash
adb devices
```

Укажи путь к APK в `tests/ui/bookmarks/config/settings.py`:

```python
_APP_PATH = r"C:\path\to\mapsme.apk"
```

Или через переменную окружения:

```bash
# Windows PowerShell
$env:APP_PATH = "C:\path\to\mapsme.apk"
```

### Запуск

```bash
# Сначала запусти Appium
appium

# Все тесты меток
pytest tests/ui/bookmarks/ --log-cli-level=INFO

# Только smoke-тесты
pytest tests/ui/bookmarks/ -m smoke

# Конкретный модуль
pytest tests/ui/bookmarks/test_bookmark_creation.py -v

# С Allure-отчётом
pytest tests/ui/bookmarks/ --alluredir=reports/allure_results
allure serve reports/allure_results
```

### Параметры подключения (bookmarks/config/settings.py)

| Параметр | Значение |
|---|---|
| Appium URL | `http://127.0.0.1:4723` |
| Platform | Android |
| App package | `com.mapswithme.maps.pro` |
| Automation | UiAutomator2 |
| noReset | `True` (сохраняет состояние приложения) |

---

## Покрытие тестами

| Область | Тестов | Статус |
|---|---|---|
| User Details | 6 | ✅ |
| Email validation | 14 | ✅ |
| User Agreement | 7 | ✅ |
| Subscription Plans | 5 | ✅ |
| Payment Methods | 7 | ✅ |
| Subscriptions | 6 | ✅ |
| Payment / Purchase | 9 | ✅ |
| UI: Subscription flow | 6 | ✅ (требует Appium) |
| UI: Создание меток | 5 | ✅ (требует устройство) |
| UI: Редактирование меток | 5 | ✅ (требует устройство) |
| UI: Удаление меток | 4 | ✅ (требует устройство) |
| UI: Управление папками | 6 | ✅ (требует устройство) |
| UI: Отображение на карте | 5 | ✅ (требует устройство) |
| UI: Поиск и сортировка | 7 | ✅ (требует устройство) |
| UI: Оффлайн / синхронизация | 5 | ✅ (требует устройство) |
