from django import forms


class SendCoinsForm(forms.Form):
    recipient_wallet = forms.CharField(label='Wallet Address', max_length=100)
    amount = forms.FloatField(label='amount')
