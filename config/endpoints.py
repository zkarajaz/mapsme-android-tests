class Endpoints:
    # Auth & Users
    AUTH = "/mapsme-auth/public/api/v1/auth"
    ACCEPT_TERMS = "/mapsme-auth/public/api/v1/users/accept-terms"
    USER_DETAILS = "/mapsme-auth/public/api/v4/users/user_details"
    
    # Subscriptions
    SUBSCRIPTIONS = "/subscription-2/public/api/v1/subscriptions"
    SUB_PLANS = "/subscription-2/public/api/v1/subscription-plans"
    PAYMENT_METHODS = "/subscription-2/public/api/v1/payment-methods"
    

    PURCHASE_NEW = "/subscription-2/public/api/v1/subscription-plans/{plan_id}/prices/{price_id}/purchase"
    PURCHASE_SAVED = "/subscription-2/public/api/v1/payment-methods/{method_id}/subscription-plans/{plan_id}/prices/{price_id}/purchase"