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
import pytest
import requests
from django.urls import reverse

from citizen_frontend.payment_providers.forms.mock_forms import (
    FAILED_PAYMENT_REQUEST,
    SUCCESSFUL_PAYMENT_REQUEST,
    MockWorldPayResponseForm,
)


@pytest.fixture
def mock_post(mocker):
    yield mocker.patch.object(requests, "post")


def test_mock_worldpay_handles_successful_payment_request(client, mock_post):
    expect_return_form = MockWorldPayResponseForm(
        {
            "cartId": SUCCESSFUL_PAYMENT_REQUEST["cartId"],
            "instId": SUCCESSFUL_PAYMENT_REQUEST["instId"],
            "amount": SUCCESSFUL_PAYMENT_REQUEST["amount"],
            "transStatus": "Y",
            "transId": "UUID",
            "callBackPW": SUCCESSFUL_PAYMENT_REQUEST["callBackPW"],
        }
    )

    response = client.post(reverse("worldpay"), data=SUCCESSFUL_PAYMENT_REQUEST)

    mock_post.assert_called()
    assert response.status_code == 200

    if expect_return_form.is_valid():
        mock_post.assert_called_with(
            "http://testserver/fake/payment/worldpayCallback", data=expect_return_form.cleaned_data
        )


def test_mock_worldpay_handles_failed_payment_request(client, mock_post):
    expect_return_form = MockWorldPayResponseForm(
        {
            "cartId": FAILED_PAYMENT_REQUEST["cartId"],
            "instId": FAILED_PAYMENT_REQUEST["instId"],
            "amount": FAILED_PAYMENT_REQUEST["amount"],
            "transStatus": "C",
            "callBackPW": FAILED_PAYMENT_REQUEST["callBackPW"],
        }
    )

    response = client.post(reverse("worldpay"), data=FAILED_PAYMENT_REQUEST)

    mock_post.assert_called()
    assert response.status_code == 200

    if expect_return_form.is_valid():
        data = expect_return_form.cleaned_data
    mock_post.assert_called_with("http://testserver/fake/payment/worldpayCallback", data=data)


def test_mock_worldpay_returns_400_invalid_request(client, mock_post):
    response = client.post(reverse("worldpay"), data={"invalid": "form format"})

    assert response.status_code == 400
