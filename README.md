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
│   └── ui/                     # UI-тесты на Appium (6 тестов)
│       └── test_ui.py
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
