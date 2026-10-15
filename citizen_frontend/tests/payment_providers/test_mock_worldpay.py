# TODO: What do I need,
#   Route to post to, think this will need to be the same as the existing app,
#         these are set at the payment account level
#   Stubbed Form response objects => looks like we handle a post request that has form data
#       Model looks like: cartID: str
#                         amount: str
#                         callbackPW: str
#                         transStatus: str
#                         transId: str | None
#                         instId: str
#   Scenarios to cover: Success => "transStatus" == "Y" this is wrapped in Seq()
#                       Failure => "transStatus" == "C" this is wrapped in Seq()
#                       Failure => CallbackPW mismatch
#   Mock requests to cover the about scenarios => again post form data
import requests
from django.urls import reverse

from citizen_frontend.payment_providers.forms.mock_forms import SUCCESSFUL_PAYMENT_REQUEST


def test_mock_worldpay_handles_successful_payment_request(client, mocker):
    mock_post = mocker.patch.object(requests, "post")

    response = client.post(reverse("worldpay"), data=SUCCESSFUL_PAYMENT_REQUEST)
    mock_post.assert_called()
    assert response.status_code == 200
