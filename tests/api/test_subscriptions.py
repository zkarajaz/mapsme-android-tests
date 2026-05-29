import json
import os
import pytest
import allure
from jsonschema import validate
from config.settings import Endpoints

SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__), "../../utils/schemas/subscriptions_schema.json"
)


@allure.feature("Подписки")
class TestSubscriptions:

    @allure.story("S-01: GET /subscriptions — 200 OK + JSON Schema")
    def test_get_subscriptions_returns_200_and_valid_schema(self, auth_client):
        """Проверяем статус, структуру ответа и соответствие JSON-схеме."""
        response = auth_client.get(Endpoints.SUBSCRIPTIONS)

        assert response.status_code == 200, (
            f"Ожидали 200, получили {response.status_code}: {response.text}"
        )
        body = response.json()
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = json.load(f)
        validate(instance=body, schema=schema)

        assert "page" in body, "В ответе отсутствует объект 'page'"
        assert "content" in body["page"], "В объекте 'page' отсутствует список 'content'"
        assert isinstance(body["page"]["content"], list), "content должен быть массивом"

    @allure.story("S-02: Подписка со статусом ACTIVE")
    def test_subscription_active_status(self, subscriptions_content):
        """Если у пользователя есть ACTIVE-подписка — проверяем её поля."""
        active = [s for s in subscriptions_content if s.get("status") == "ACTIVE"]
        if not active:
            pytest.skip("В тестовом аккаунте нет подписок со статусом ACTIVE")

        sub = active[0]
        assert sub.get("id"), "У ACTIVE-подписки отсутствует поле id"
        assert sub["status"] == "ACTIVE"

    @allure.story("S-03: Подписка со статусом INITIATED — структура объекта корректна")
    def test_subscription_initiated_structure(self, subscriptions_content):
        """
        INITIATED-подписка существует и содержит обязательные поля.
        paymentOrderPaymentConfirmationUrl присутствует только если был создан платёжный ордер
        (YooKassa redirect-флоу). Для Google Pay / App Store этого поля нет — это нормально.
        """
        initiated = [s for s in subscriptions_content if s.get("status") == "INITIATED"]
        if not initiated:
            pytest.skip("В тестовом аккаунте нет подписок со статусом INITIATED")

        sub = initiated[0]
        assert sub.get("id"), "У INITIATED-подписки отсутствует поле id"
        assert sub["status"] == "INITIATED"
        assert "planId" in sub, "У INITIATED-подписки отсутствует planId"
        assert "planName" in sub, "У INITIATED-подписки отсутствует planName"

        # Если ссылка на оплату есть — она должна быть валидным URL
        confirmation_url = sub.get("paymentOrderPaymentConfirmationUrl")
        if confirmation_url:
            assert confirmation_url.startswith("http"), (
                f"paymentOrderPaymentConfirmationUrl должен быть URL: {confirmation_url}"
            )

    @allure.story("S-04: content — всегда массив (в том числе пустой)")
    def test_subscriptions_content_is_list(self, subscriptions_content):
        assert isinstance(subscriptions_content, list), (
            "content должен быть массивом даже при отсутствии подписок"
        )

    @allure.story("S-05: Каждая подписка содержит обязательные поля")
    def test_each_subscription_has_required_fields(self, subscriptions_content):
        if not subscriptions_content:
            pytest.skip("У пользователя нет подписок — нечего валидировать")

        for sub in subscriptions_content:
            assert "id" in sub, f"Подписка без поля id: {sub}"
            assert "status" in sub, f"Подписка без поля status: {sub}"

    @allure.story("S-06: GET /subscriptions с некорректным параметром → 4xx")
    def test_subscriptions_invalid_param_returns_4xx(self, auth_client):
        """Невалидный pageSize=-1 должен вернуть клиентскую ошибку."""
        response = auth_client.get(Endpoints.SUBSCRIPTIONS + "?pageSize=-1")
        assert response.status_code in range(400, 500), (
            f"Ожидали 4xx, получили {response.status_code}"
        )
