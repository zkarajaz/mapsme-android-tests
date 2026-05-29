import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Базовые настройки
    BASE_URL = os.getenv("BASE_URL", "https://api.maps.me")
    TEST_USER_JWT = os.getenv("TEST_USER_JWT", "твой_тестовый_токен_здесь")
    TIMEOUT = 10
    # Тестовая карта для создания INITIATED-подписки через YooMoney
    TEST_CARD_NUMBER = os.getenv("TEST_CARD_NUMBER", "")
    TEST_CARD_EXPIRY = os.getenv("TEST_CARD_EXPIRY", "")  # MMYY, напр. "1226"
    TEST_CARD_CVC    = os.getenv("TEST_CARD_CVC", "")

class Endpoints:
    # Auth & User
    AUTH             = "/mapsme-auth/public/api/v1/auth"
    AUTH_PHONE       = "/mapsme-auth/public/api/v1/auth/by-phone/complete"
    ACCEPT_TERMS     = "/mapsme-auth/public/api/v1/users/accept-terms"
    USER_DETAILS     = "/mapsme-auth/public/api/v4/users/user_details"
    
    # Subscriptions
    SUBSCRIPTIONS    = "/subscription-2/public/api/v1/subscriptions"
    SUB_PLANS        = "/subscription-2/public/api/v1/subscription-plans"
    PAYMENT_METHODS  = "/subscription-2/public/api/v1/payment-methods"
    
    # Purchase
    PURCHASE_NEW     = "/subscription-2/public/api/v1/subscription-plans/{plan_id}/prices/{price_id}/purchase"
    PURCHASE_SAVED   = "/subscription-2/public/api/v1/payment-methods/{method_id}/subscription-plans/{plan_id}/prices/{price_id}/purchase"