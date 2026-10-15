from django.urls import path

from citizen_frontend.payment_providers.mock_providers import mock_worldpay, mock_worldpay_callback

urlpatterns = [
    path("payment/worldpay", mock_worldpay.handle_payment, name="worldpay"),
    path("payment/worldpayCallback", mock_worldpay_callback.callback, name="worldpayCallback"),
]
