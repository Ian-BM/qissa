from django import forms

from .models import Chapter, Story, StoryCategory

class StoryForm(forms.ModelForm):
    new_category_name = forms.CharField(
        required=False,
        max_length=80,
        label="Create category",
        widget=forms.TextInput(
            attrs={"placeholder": "Type a new category name (optional)"}
        ),
        help_text="If you type a name here, it will be created and used for this story.",
    )

    class Meta:
        model = Story
        fields = ["title", "category", "description", "price", "cover", "is_published"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Story title"}),
            "category": forms.Select(),
            "description": forms.Textarea(attrs={"rows": 5}),
            "price": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = StoryCategory.objects.all()
        self.fields["category"].required = False
        self.order_fields(
            ["title", "category", "new_category_name", "description", "price", "cover", "is_published"]
        )

    def save(self, commit=True):
        story = super().save(commit=False)
        category_name = (self.cleaned_data.get("new_category_name") or "").strip()
        if category_name:
            category, _ = StoryCategory.objects.get_or_create(name=category_name)
            story.category = category
        elif self.cleaned_data.get("category"):
            story.category = self.cleaned_data["category"]

        if commit:
            story.save()
            self.save_m2m()
        return story

class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ["title", "content", "order"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Chapter title"}),
            "content": forms.Textarea(attrs={"rows": 10}),
        }
