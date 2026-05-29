import pytest
import allure
from config.settings import Endpoints


@allure.feature("Планы подписки")
class TestSubscriptionPlans:

    @allure.story("P-01: GET /subscription-plans — 200 OK")
    def test_get_subscription_plans_returns_200(self, auth_client):
        response = auth_client.get(Endpoints.SUB_PLANS)

        assert response.status_code == 200, (
            f"Ожидали 200, получили {response.status_code}: {response.text}"
        )

    @allure.story("P-02: Ответ содержит массив планов")
    def test_subscription_plans_has_content(self, plans_content):
        assert isinstance(plans_content, list), "Список планов должен быть массивом"
        assert len(plans_content) > 0, "Список планов не должен быть пустым"

    @allure.story("P-03: Каждый план содержит обязательные поля")
    def test_each_plan_has_required_fields(self, plans_content):
        if not plans_content:
            pytest.skip("Нет планов для проверки")

        for plan in plans_content:
            assert "id" in plan, f"Планo без поля id: {plan}"
            assert "prices" in plan, f"У плана {plan.get('id')} нет поля prices"
            assert isinstance(plan["prices"], list), "prices должен быть массивом"
            assert len(plan["prices"]) > 0, f"У плана {plan.get('id')} пустой массив prices"

    @allure.story("P-04: Каждая цена плана содержит id, сумму и валюту")
    def test_each_price_has_id_and_amount(self, plans_content):
        if not plans_content:
            pytest.skip("Нет планов для проверки")

        for plan in plans_content:
            for price in plan.get("prices", []):
                assert "id" in price, (
                    f"У цены плана {plan.get('id')} отсутствует поле id"
                )
                assert "priceAmount" in price, (
                    f"У цены плана {plan.get('id')} отсутствует поле priceAmount: {price}"
                )
                assert "priceCurrency" in price, (
                    f"У цены плана {plan.get('id')} отсутствует поле priceCurrency"
                )

    @allure.story("P-05: GET /subscription-plans с сортировкой — 200 OK")
    def test_get_plans_with_sort_params(self, auth_client):
        params = "?pageNumber=0&pageSize=10&sort=name,asc"
        response = auth_client.get(f"{Endpoints.SUB_PLANS}{params}")

        assert response.status_code == 200, (
            f"Ожидали 200 с параметрами сортировки, получили {response.status_code}"
        )
