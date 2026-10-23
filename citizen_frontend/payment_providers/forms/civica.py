from django import forms


class CivicaRequestForm(forms.Form):
    CallingApplicationID = forms.CharField()
    ReturnURL = forms.CharField()
    PaymentTotal = forms.CharField()
    BackButtonURL = forms.CharField()
    PaymentSourceCode = forms.CharField(initial="01")
    Payment_1 = forms.CharField()
    PaymentData_1 = forms.CharField()
    CallingApplicationTransactionReference = forms.CharField()


class CivicaResponseForm(forms.Form):
    ResponseCode = forms.CharField()
    ResponseDescription = forms.CharField(required=False)
    PaymentAuthorisationCode = forms.CharField(required=False)
    IncomeManagementReceiptNumber = forms.CharField(required=False)
    OriginatorsReference = forms.CharField(required=False)
    CallingApplicationTransactionReference = forms.CharField(required=False)
    PaymentAmount = forms.CharField(required=False)
