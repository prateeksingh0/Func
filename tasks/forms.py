from django import forms
import re

class YouTubeForm(forms.Form):
    url = forms.URLField(label="YouTube URL", max_length=200)
    download_type = forms.ChoiceField(
        choices=[('video', 'Video'), ('audio', 'Audio')],
        widget=forms.RadioSelect
    )
