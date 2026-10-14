from django import forms


class MockWorldPayRequestForm(forms.Form):
    cartId = forms.CharField()
    callBackPW = forms.CharField()
    amount = forms.CharField()
    currency = forms.CharField()
    signature = forms.CharField()
    desc = forms.CharField()
    authValidTo = forms.CharField()
    acctId = forms.JSONField()
    instId = forms.CharField()


class MockWorldPayResponseForm(forms.Form):
    cartId = forms.CharField()
    instId = forms.CharField()
    amount = forms.CharField()
    callBackPW = forms.CharField()
    transStatus = forms.CharField()
    transId = forms.CharField(required=False)
