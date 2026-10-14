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
from copy import deepcopy

# unsure of data structure of acctId
SUCCESSFUL_PAYMENT = {
    "cartId": "12345",
    "callBackPW": "supersecret",
    "amount": "10",
    "currency": "GBP",
    "signature": "MD5 signature created from various variables",
    "desc": "description or purchase code",
    "authValidTo": "string time tha auth is valid to",
    "acctId": {"details": "from", "payment": "parameters"},
    "instId": "merchant id on payment account",
}

FAILED_PAYMENT = deepcopy(SUCCESSFUL_PAYMENT)
FAILED_PAYMENT["cartId"] = "67890"

NON_MATCHING_PASSWORD_PAYMENT = deepcopy(SUCCESSFUL_PAYMENT)
NON_MATCHING_PASSWORD_PAYMENT["callBackPW"] = "not matching"
NON_MATCHING_PASSWORD_PAYMENT["signature"] = "not matching"
