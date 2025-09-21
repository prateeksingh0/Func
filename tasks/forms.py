from django import forms

class YouTubeForm(forms.Form):
    url = forms.URLField(label="YouTube URL", max_length=200,widget=forms.TextInput(attrs={'placeholder': 'Enter YouTube video URL'}),)
    download_type = forms.ChoiceField(
        choices=[('video', 'Video'), ('audio', 'Audio')],
        widget=forms.RadioSelect,
        label="Select Download Type"
    )
