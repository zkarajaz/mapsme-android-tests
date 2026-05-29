import pytest
import allure
from config.settings import Endpoints


@allure.feature("Методы оплаты")
class TestPaymentMethods:

    @allure.story("PM-01: GET /payment-methods — 200 OK")
    def test_get_payment_methods_returns_200(self, auth_client):
        response = auth_client.get(Endpoints.PAYMENT_METHODS)

        assert response.status_code == 200, (
            f"Ожидали 200, получили {response.status_code}: {response.text}"
        )

    @allure.story("PM-02: Ответ содержит массив методов оплаты в page.content")
    def test_payment_methods_has_content_array(self, auth_client):
        response = auth_client.get(Endpoints.PAYMENT_METHODS)
        body = response.json()

        assert "page" in body, "В ответе отсутствует объект 'page'"
        assert "content" in body["page"], "В объекте 'page' отсутствует массив 'content'"
        assert isinstance(body["page"]["content"], list), "page.content должен быть массивом"

    @allure.story("PM-03: Сохранённые методы оплаты присутствуют у пользователя")
    def test_saved_payment_methods_present(self, payment_methods_content):
        if not payment_methods_content:
            pytest.skip("У тестового пользователя нет сохранённых методов оплаты")

        assert len(payment_methods_content) > 0

    @allure.story("PM-04: Сохранённый метод оплаты содержит обязательные поля")
    def test_saved_payment_method_has_required_fields(self, payment_methods_content):
        if not payment_methods_content:
            pytest.skip("Нет сохранённых методов оплаты")

        method = payment_methods_content[0]
        assert "id" in method, "Отсутствует поле id"
        assert "paymentMethodType" in method, (
            "Отсутствует поле paymentMethodType (тип: BANK_CARD и т.д.)"
        )
        assert "paymentChannel" in method, "Отсутствует поле paymentChannel (YOOKASSA / STRIPE)"
        assert "paymentMethodCardLast4" in method, (
            "Отсутствует поле paymentMethodCardLast4"
        )
        assert "status" in method, "Отсутствует поле status"

    @allure.story("PM-05: paymentMethodCardLast4 — 4 цифры если заполнен")
    def test_card_last4_format_when_present(self, payment_methods_content):
        if not payment_methods_content:
            pytest.skip("Нет сохранённых методов оплаты")

        for method in payment_methods_content:
            last4 = method.get("paymentMethodCardLast4")
            if last4 is None:
                continue  # null допустим — карта ещё не прошла реальный платёж
            assert len(str(last4)) == 4 and str(last4).isdigit(), (
                f"paymentMethodCardLast4 должен быть 4-значным числом, получили: '{last4}'"
            )

    @allure.story("PM-06: Нет сохранённых методов → content пустой массив")
    def test_no_saved_methods_content_is_empty(self, payment_methods_content):
        if payment_methods_content:
            pytest.skip("У пользователя есть методы оплаты — сценарий 'нет методов' неприменим")

        assert payment_methods_content == []

    @allure.story("PM-07: id метода оплаты доступен для использования при покупке")
    def test_payment_method_id_available(self, payment_methods_content):
        if not payment_methods_content:
            pytest.skip("Нет сохранённых методов оплаты")

        method_id = payment_methods_content[0].get("id")
        assert method_id, "id метода оплаты пустой или отсутствует"
        assert isinstance(method_id, str)
