from django.urls import path

from citizen_frontend.payment_providers.mock_providers import mock_worldpay, mock_worldpay_callback
from citizen_frontend.payment_providers.mock_providers.access_paysuite import mock_access_paysuite
from citizen_frontend.payment_providers.mock_providers.northgate import mock_northgate

urlpatterns = [
    path("payment/worldpay", mock_worldpay.handle_payment, name="worldpay"),
    path("payment/worldpayCallback", mock_worldpay_callback.callback, name="worldpayCallback"),
    path("payment/northgate", mock_northgate.handle_payment, name="northgate"),
    path("payment/northgateCallback", mock_northgate.callback, name="northgateCallback"),
    path("payment/access-paysuite-sucess", mock_access_paysuite.handle_success, name="access_paysuite_success"),
    path("payment/accessPaysuiteCallback", mock_access_paysuite.call_back, name="accessPaysuiteCallback"),
]
