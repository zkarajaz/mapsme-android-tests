import re
import pytest
import allure
from config.settings import Endpoints

EMAIL_REGEX = r'^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$'

VALID_EMAILS = [
    "user@example.com",
    "user.name+tag@domain.co.uk",
    "a@b.ru",
    "test123@test-domain.org",
]

INVALID_EMAILS = [
    "notanemail",
    "@nodomain.com",
    "missing@.com",
    "spaces in@email.com",
    "no-tld@domain",
    "",
]


@allure.feature("Email")
class TestEmail:

    @allure.story("E-01: user_details возвращает поле email")
    def test_email_field_exists_in_user_details(self, auth_client):
        response = auth_client.get(Endpoints.USER_DETAILS)
        assert response.status_code == 200
        body = response.json()
        assert "email" in body, "Поле email отсутствует в ответе user_details"

    @allure.story("E-02: Email присутствует у пользователя")
    def test_email_is_present(self, user_details):
        if user_details.get("email") is None:
            pytest.skip("Email отсутствует в тестовом аккаунте")

        assert user_details["email"] is not None
        assert isinstance(user_details["email"], str)

    @allure.story("E-03: Email отсутствует → поле равно null")
    def test_email_is_null(self, user_details):
        if user_details.get("email") is not None:
            pytest.skip("Email присутствует в тестовом аккаунте")

        assert user_details["email"] is None

    @allure.story("E-04: Email из user_details проходит валидацию формата")
    def test_real_email_matches_pattern(self, user_details):
        email = user_details.get("email")
        if email is None:
            pytest.skip("Email отсутствует — нечего валидировать")

        assert re.match(EMAIL_REGEX, email), (
            f"Email '{email}' из user_details не соответствует допустимому формату"
        )

    @allure.story("E-05: Валидные email-форматы принимаются")
    @pytest.mark.parametrize("email", VALID_EMAILS)
    def test_valid_email_formats(self, email):
        assert re.match(EMAIL_REGEX, email), (
            f"Email '{email}' должен быть валидным, но не прошёл проверку"
        )

    @allure.story("E-06: Невалидные email-форматы отклоняются")
    @pytest.mark.parametrize("email", INVALID_EMAILS)
    def test_invalid_email_formats(self, email):
        assert not re.match(EMAIL_REGEX, email), (
            f"Email '{email}' должен быть невалидным, но прошёл проверку"
        )
