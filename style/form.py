from django import forms
from .models import Style


class StyleForm(forms.ModelForm):
    class Meta:
        model = Style
        fields = [
            "title",
            "content",
            "image",
            "tag",
        ]
