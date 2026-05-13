from django import forms
from .models import Question, Answer, Tag


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        label='Tags',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form_input',
            'placeholder': 'Enter tags separated by commas'
        }),
    )

    class Meta:
        model = Question
        fields = ['title', 'content']
        labels = {
            'title': 'Title',
            'content': 'Question text',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form_input',
                'placeholder': 'Enter title here'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form_text_input',
                'placeholder': 'Enter text here',
            }),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or not title.strip():
            raise forms.ValidationError("The title can't be empty!")
        return title.strip()

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or not content.strip():
            raise forms.ValidationError("The text can't be empty!")
        return content.strip()

    def clean_tags(self):
        tags_str = self.cleaned_data.get('tags', '')
        if not tags_str:
            return []

        tag_names = [tag.strip().lower() for tag in tags_str.split(',') if tag.strip()]
        return tag_names[:5]

    def save(self, commit=True):
        question = super().save(commit=False)

        if commit:
            question.save()
            tag_names = self.cleaned_data.get('tags', [])
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                question.tags.add(tag)

        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form_ans_text_input',
                'placeholder': 'Enter your answer here',
            }),
        }

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or not content.strip():
            raise forms.ValidationError("The answer can't be empty!")
        return content.strip()

