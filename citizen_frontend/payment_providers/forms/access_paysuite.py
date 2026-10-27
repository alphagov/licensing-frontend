from django import forms


# TODO add widget hidden form input to form fields?
class AccessPaysuiteRequestForm(forms.Form):
    portal_id = forms.CharField()
    hash = forms.CharField()
    portalReq = forms.CharField()
    schemaId = forms.CharField(initial="APPXML_V2")


class AccessPaymentProviderResponseForm(forms.Form):
    hash = forms.CharField()
    status = forms.CharField()
