import pytest
import allure
from config.settings import Endpoints


@allure.feature("Пользовательское соглашение")
class TestUserAgreement:

    @allure.story("UA-01: has_accepted_terms = true → поле корректно отражает статус")
    def test_terms_accepted_state(self, user_details):
        if not user_details.get("has_accepted_terms"):
            pytest.skip("Тестовый аккаунт не принял соглашение — тест accepted=True пропущен")

        assert user_details["has_accepted_terms"] is True

    @allure.story("UA-02: has_accepted_terms = false → поле корректно отражает статус")
    def test_terms_not_accepted_state(self, user_details):
        if user_details.get("has_accepted_terms"):
            pytest.skip("Тестовый аккаунт уже принял соглашение — тест accepted=False пропущен")

        assert user_details["has_accepted_terms"] is False

    @allure.story("UA-03: has_accepted_terms = false → email == null (нужен ввод email)")
    def test_terms_not_accepted_email_is_null(self, user_details):
        if user_details.get("has_accepted_terms"):
            pytest.skip("Тестовый аккаунт принял соглашение — сценарий не применим")

        assert user_details.get("email") is None, (
            "При has_accepted_terms=False ожидали email == null"
        )

    @allure.story("UA-04: PATCH /accept-terms → 200 OK (идемпотентный вызов)")
    def test_accept_terms_returns_200(self, auth_client):
        response = auth_client.patch(Endpoints.ACCEPT_TERMS)
        assert response.status_code == 200, (
            f"Ожидали 200 от PATCH /accept-terms, получили {response.status_code}: {response.text}"
        )

    @allure.story("UA-05: После PATCH /accept-terms — has_accepted_terms = true")
    def test_after_accept_terms_flag_is_true(self, auth_client):
        patch_response = auth_client.patch(Endpoints.ACCEPT_TERMS)
        assert patch_response.status_code == 200, (
            f"PATCH /accept-terms вернул {patch_response.status_code}"
        )

        get_response = auth_client.get(Endpoints.USER_DETAILS)
        assert get_response.status_code == 200
        assert get_response.json()["has_accepted_terms"] is True, (
            "После PATCH /accept-terms ожидали has_accepted_terms=True"
        )

    @allure.story("UA-06: user_details возвращает данные, необходимые для отображения соглашения")
    def test_user_details_contains_agreement_fields(self, user_details):
        """
        API возвращает has_accepted_terms (bool) и hasAcceptedRecurringPaymentTerms (bool).
        Ссылки на документы (terms_url, privacy_url) — статические, находятся на UI-уровне,
        API их не возвращает. Проверяем, что API корректно отдаёт все agreement-флаги.
        """
        assert "has_accepted_terms" in user_details, (
            "Поле has_accepted_terms отсутствует в user_details"
        )
        assert "hasAcceptedRecurringPaymentTerms" in user_details, (
            "Поле hasAcceptedRecurringPaymentTerms отсутствует в user_details"
        )
        assert isinstance(user_details["has_accepted_terms"], bool)
        assert isinstance(user_details["hasAcceptedRecurringPaymentTerms"], bool)

    @allure.story("UA-07: Покупка без принятия соглашения → ошибка")
    def test_cannot_purchase_without_accepting_terms(self, auth_client, user_details, plans_content):
        if user_details.get("has_accepted_terms"):
            pytest.skip(
                "Тестовый аккаунт уже принял соглашение — "
                "сценарий 'покупка без соглашения' недоступен"
            )
        if not plans_content:
            pytest.skip("Нет доступных планов подписки для теста")

        plan = plans_content[0]
        endpoint = Endpoints.PURCHASE_NEW.format(
            plan_id=plan["id"],
            price_id=plan["prices"][0]["id"],
        )
        response = auth_client.post(
            endpoint,
            json={"email": "test@test.ru", "paymentConfirmationReturnUrl": "app://return"},
        )

        assert response.status_code in [400, 403, 422], (
            f"Ожидали ошибку при покупке без принятия соглашения, "
            f"получили {response.status_code}"
        )
        body = response.json()
        assert body, "Ожидалось тело ответа с описанием ошибки"
