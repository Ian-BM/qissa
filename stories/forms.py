from django import forms
from .models import Story

class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ["title", "description", "cover", "is_published"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Story title"}),
            "description": forms.Textarea(attrs={"rows": 5}),
        }


from django import forms
from .models import Chapter

class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ["title", "content", "order"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Chapter title"}),
            "content": forms.Textarea(attrs={"rows": 10}),
        }
