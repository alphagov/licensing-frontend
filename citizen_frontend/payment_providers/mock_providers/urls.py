from django.urls import path

from citizen_frontend.payment_providers.mock_providers import mock_worldpay, mock_worldpay_callback
from citizen_frontend.payment_providers.mock_providers.access_paysuite import mock_access_paysuite
from citizen_frontend.payment_providers.mock_providers.northgate import mock_northgate

urlpatterns = [
    path("payment/worldpay", mock_worldpay.handle_payment, name="worldpay"),
    path("payment/worldpayCallback", mock_worldpay_callback.callback, name="worldpayCallback"),
    path("payment/northgate-success", mock_northgate.handle_payment, name="northgate_success"),
    path("payment/northgate-failure", mock_northgate.handle_payment, name="northgate_failure"),
    path("payment/northgate-cancel", mock_northgate.handle_payment, name="northgate_cancel"),
    path("payment/northgate-error", mock_northgate.handle_payment, name="northgate_error"),
    path("payment/northgateCallback", mock_northgate.callback, name="northgateCallback"),
    path("payment/access-paysuite-success", mock_access_paysuite.handle_success, name="access_paysuite_success"),
    path(
        "payment/access-paysuite-known-failure",
        mock_access_paysuite.handle_known_failure,
        name="access_paysuite_known_failure",
    ),
    path(
        "payment/access-paysuite-unknown-failure",
        mock_access_paysuite.handle_unknown_failure,
        name="access_paysuite_unknown_failure",
    ),
    path(
        "payment/access-paysuite-card-declined",
        mock_access_paysuite.handle_card_declined,
        name="access_paysuite_card_declined",
    ),
    path("payment/accessPaysuiteCallback", mock_access_paysuite.call_back, name="accessPaysuiteCallback"),
]
