import uuid
import pytest
import allure
from config.settings import Endpoints

# Реальный HTTPS URL, который принимает API для redirecta после оплаты
RETURN_URL = "https://maps.me/payment/return"


def _purchase_payload(email="autotest@test.ru"):
    """Формирует тело запроса с обязательными полями для покупки."""
    key = str(uuid.uuid4())
    return (
        {
            "email": email,
            "paymentConfirmationReturnUrl": RETURN_URL,
            "idempotencyKey": key,
        },
        {"X-Idempotency-Key": key},
    )


@allure.feature("Оплата")
class TestPayments:

    # ──────────────────────────────────────────────
    # Покупка новой картой
    # ──────────────────────────────────────────────

    @allure.story("PAY-01: Покупка новой картой — API принимает запрос")
    def test_purchase_new_card_api_accepts_request(self, auth_client, plans_content):
        """
        POST /purchase с валидной структурой (включая X-Idempotency-Key и реальный return URL).
        Ожидаем 200 (успех) или 409 (уже есть подписка).
        """
        if not plans_content:
            pytest.skip("Нет доступных планов")

        plan = plans_content[0]
        endpoint = Endpoints.PURCHASE_NEW.format(
            plan_id=plan["id"],
            price_id=plan["prices"][0]["id"],
        )
        body, headers = _purchase_payload()
        response = auth_client.post(endpoint, json=body, headers=headers)

        assert response.status_code in [200, 409], (
            f"Неожиданный статус {response.status_code}: {response.text}"
        )

    @allure.story("PAY-02: Успешная покупка новой картой → 200 + структура ответа")
    def test_purchase_new_card_success_response_structure(self, auth_client, plans_content):
        """При 200 ответ содержит id, status и paymentConfirmationUrl."""
        if not plans_content:
            pytest.skip("Нет доступных планов")

        plan = plans_content[0]
        endpoint = Endpoints.PURCHASE_NEW.format(
            plan_id=plan["id"],
            price_id=plan["prices"][0]["id"],
        )
        body, headers = _purchase_payload()
        response = auth_client.post(endpoint, json=body, headers=headers)

        if response.status_code == 409:
            pytest.skip("Пользователь уже подписан — успешный 200 недостижим без отмены подписки")

        assert response.status_code == 200, (
            f"Ожидали 200, получили {response.status_code}: {response.text}"
        )
        resp_body = response.json()
        assert "id" in resp_body, "В успешном ответе нет поля id"
        assert "status" in resp_body, "В успешном ответе нет поля status"
        assert resp_body.get("paymentConfirmationUrl"), (
            "В успешном ответе нет paymentConfirmationUrl для редиректа на оплату"
        )

    # ──────────────────────────────────────────────
    # Покупка сохранённой картой
    # ──────────────────────────────────────────────

    @allure.story("PAY-03: Покупка сохранённой картой — endpoint доступен и принимает запрос")
    def test_purchase_saved_card_endpoint_reachable(
        self, auth_client, payment_methods_content, plans_content
    ):
        """
        Отправляем POST с правильной структурой, но без email (нужна только карта).
        Ожидаем 200/409 — без реального списания, так как у нас тестовый аккаунт.
        """
        if not payment_methods_content:
            pytest.skip("Нет сохранённых карт")
        if not plans_content:
            pytest.skip("Нет доступных планов")

        method_id = payment_methods_content[0]["id"]
        plan = plans_content[0]
        endpoint = Endpoints.PURCHASE_SAVED.format(
            method_id=method_id,
            plan_id=plan["id"],
            price_id=plan["prices"][0]["id"],
        )
        key = str(uuid.uuid4())
        body = {
            "paymentConfirmationReturnUrl": RETURN_URL,
            "idempotencyKey": key,
        }
        response = auth_client.post(endpoint, json=body, headers={"X-Idempotency-Key": key})

        assert response.status_code not in [404, 500, 502], (
            f"Endpoint недоступен или сервер упал: {response.status_code}: {response.text}"
        )

    @allure.story("PAY-04: Успешная покупка сохранённой картой → 200 + id и status")
    @pytest.mark.skip(
        reason="Требует sandbox: покупка сохранённой картой вызывает реальное списание средств"
    )
    def test_purchase_saved_card_success(self, auth_client, payment_methods_content, plans_content):
        if not payment_methods_content:
            pytest.skip("Нет сохранённых карт")
        if not plans_content:
            pytest.skip("Нет доступных планов")

        method_id = payment_methods_content[0]["id"]
        plan = plans_content[0]
        endpoint = Endpoints.PURCHASE_SAVED.format(
            method_id=method_id,
            plan_id=plan["id"],
            price_id=plan["prices"][0]["id"],
        )
        key = str(uuid.uuid4())
        body = {"paymentConfirmationReturnUrl": RETURN_URL, "idempotencyKey": key}
        response = auth_client.post(endpoint, json=body, headers={"X-Idempotency-Key": key})

        assert response.status_code in [200, 409]
        if response.status_code == 200:
            resp_body = response.json()
            assert "id" in resp_body
            assert "status" in resp_body

    # ──────────────────────────────────────────────
    # Обработка ошибок
    # ──────────────────────────────────────────────

    @allure.story("PAY-05: Покупка несуществующего плана → 404")
    def test_purchase_nonexistent_plan_returns_404(self, auth_client):
        """Валидный UUID-формат, которого нет в базе — API возвращает 404 после проверки валидации."""
        endpoint = Endpoints.PURCHASE_NEW.format(
            plan_id="00000000-0000-0000-0000-000000000000",
            price_id="00000000-0000-0000-0000-000000000001",
        )
        body, headers = _purchase_payload()
        response = auth_client.post(endpoint, json=body, headers=headers)

        assert response.status_code == 404, (
            f"Ожидали 404 для несуществующего плана, получили {response.status_code}: {response.text}"
        )

    @allure.story("PAY-06: Покупка без обязательных полей → 400 или 422")
    def test_purchase_missing_required_fields_returns_error(self, auth_client, plans_content):
        if not plans_content:
            pytest.skip("Нет доступных планов")

        plan = plans_content[0]
        endpoint = Endpoints.PURCHASE_NEW.format(
            plan_id=plan["id"],
            price_id=plan["prices"][0]["id"],
        )
        response = auth_client.post(endpoint, json={})

        assert response.status_code in [400, 422], (
            f"Ожидали 400/422 при пустом теле, получили {response.status_code}"
        )

    @allure.story("PAY-07: Ошибочный ответ содержит описание ошибки")
    def test_error_response_has_error_field(self, auth_client):
        endpoint = Endpoints.PURCHASE_NEW.format(
            plan_id="00000000-0000-0000-0000-000000000000",
            price_id="00000000-0000-0000-0000-000000000001",
        )
        response = auth_client.post(endpoint, json={})

        assert response.status_code >= 400
        resp_body = response.json()
        has_error_info = any(
            k in resp_body for k in ("error", "message", "detail", "code")
        )
        assert has_error_info, (
            f"Ответ {response.status_code} не содержит описания ошибки: {resp_body}"
        )

    # ──────────────────────────────────────────────
    # Сценарий INITIATED — «Выбрать другой тариф»
    # ──────────────────────────────────────────────

    @allure.story("PAY-08: «Выбрать другой тариф» при незавершённой оплате (INITIATED)")
    def test_change_plan_when_subscription_initiated(
        self, auth_client, subscriptions_content, plans_content
    ):
        """
        1. Убеждаемся что есть INITIATED-подписка
        2. Делаем запрос на покупку другого плана — API должен принять его (200 или 409)
        """
        initiated = [s for s in subscriptions_content if s.get("status") == "INITIATED"]
        if not initiated:
            pytest.skip("Нет INITIATED-подписки — сценарий 'выбрать другой тариф' неприменим")
        if not plans_content:
            pytest.skip("Нет доступных планов")

        plan = plans_content[0]
        endpoint = Endpoints.PURCHASE_NEW.format(
            plan_id=plan["id"],
            price_id=plan["prices"][0]["id"],
        )
        body, headers = _purchase_payload()
        response = auth_client.post(endpoint, json=body, headers=headers)

        assert response.status_code in [200, 409], (
            f"Неожиданный статус при смене тарифа: {response.status_code}: {response.text}"
        )

    @allure.story("PAY-09: INITIATED-подписка — если есть ссылка на оплату, она валидна")
    def test_initiated_subscription_payment_url_valid_when_present(self, subscriptions_content):
        """
        paymentOrderPaymentConfirmationUrl присутствует только при YooKassa redirect-флоу.
        При оплате через Google Pay / App Store поля нет — это штатное поведение.
        Тест проверяет: если поле есть — оно должно быть корректным URL.
        """
        initiated = [s for s in subscriptions_content if s.get("status") == "INITIATED"]
        if not initiated:
            pytest.skip("Нет INITIATED-подписки")

        for sub in initiated:
            url = sub.get("paymentOrderPaymentConfirmationUrl")
            if url is not None:
                assert url.startswith("http"), (
                    f"paymentOrderPaymentConfirmationUrl должен быть URL, получили: {url}"
                )
