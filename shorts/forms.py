from django import forms

from .models import ShortStory


class ShortStoryForm(forms.ModelForm):
    class Meta:
        model = ShortStory
        fields = [
            "title",
            "category",
            "content",
            "excerpt",
            "cover_image",
            "featured",
            "published",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Short story title"}),
            "content": forms.Textarea(attrs={"rows": 14}),
            "excerpt": forms.Textarea(attrs={"rows": 3}),
        }
