from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].empty_label = "Группа не выбрана"

    class Meta:
        model = Post
        help_texts = {'group': 'Выберите группу',
                      'text': 'Введите ссообщение',
                      'image': 'Изображение'}
        fields = ['text', 'group', 'image']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
