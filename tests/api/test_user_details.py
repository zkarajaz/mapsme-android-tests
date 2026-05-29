import pytest
import allure
from config.settings import Endpoints


@allure.feature("Данные пользователя (user_details)")
class TestUserDetails:

    @allure.story("UD-01: GET /user_details — 200 OK")
    def test_get_user_details_returns_200(self, auth_client):
        response = auth_client.get(Endpoints.USER_DETAILS)

        assert response.status_code == 200, (
            f"Ожидали 200, получили {response.status_code}: {response.text}"
        )

    @allure.story("UD-02: Ответ содержит обязательные поля")
    def test_user_details_has_required_fields(self, user_details):
        assert "has_accepted_terms" in user_details, (
            "Поле has_accepted_terms отсутствует в ответе"
        )
        assert "email" in user_details, "Поле email отсутствует в ответе"

    @allure.story("UD-03: has_accepted_terms — булево значение")
    def test_has_accepted_terms_is_boolean(self, user_details):
        assert isinstance(user_details["has_accepted_terms"], bool), (
            f"has_accepted_terms должен быть boolean, получили: "
            f"{type(user_details['has_accepted_terms'])}"
        )

    @allure.story("UD-04: email — строка или null")
    def test_email_field_type(self, user_details):
        email = user_details.get("email")
        assert email is None or isinstance(email, str), (
            f"email должен быть строкой или null, получили: {type(email)}"
        )

    @allure.story("UD-05: Если email присутствует — он содержит символ @")
    def test_email_format_when_present(self, user_details):
        email = user_details.get("email")
        if email is None:
            pytest.skip("Email отсутствует у тестового пользователя")

        assert "@" in email, f"Email '{email}' не содержит символ @"
        assert "." in email.split("@")[-1], f"Email '{email}' не содержит домен с точкой"

    @allure.story("UD-06: Если email отсутствует — has_accepted_terms тоже False")
    def test_no_email_correlates_with_terms_not_accepted(self, user_details):
        if user_details.get("email") is not None:
            pytest.skip("У тестового пользователя есть email — сценарий 'нет email' неприменим")

        assert user_details["has_accepted_terms"] is False, (
            "При отсутствии email ожидали has_accepted_terms=False"
        )
