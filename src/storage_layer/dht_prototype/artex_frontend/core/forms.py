from django import forms


class SendCoinsForm(forms.Form):
    recipient_wallet = forms.CharField(label='Wallet Address', max_length=100)
    amount = forms.FloatField(label='amount')


class ArtworkRegistrationForm(forms.Form):
    image_data = forms.FileField()
    # artist_name = forms.CharField(label='Artist', max_length=200)
    # artist_website = forms.CharField(label='Website', max_length=200)
    # artist_written_statement = forms.CharField(label='Written statement', max_length=200)
    # artwork_title = forms.CharField(label='Title', max_length=200)
    # artwork_series_name = forms.CharField(label='Series Name', max_length=200)
    # artwork_creation_video_youtube_url = forms.CharField(label='youtube video url', max_length=200)
    # artwork_keyword_set = forms.CharField(label='Keywords', max_length=200)
    # total_copies = forms.FloatField(label='Total Copies')
