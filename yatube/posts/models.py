from core.models import CreatedModel
from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200,
                             verbose_name='Название группы',
                             help_text='Указать название группы')
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name='Описание',
                                   help_text='Описание группы')

    class Meta:
        verbose_name = 'Группу'
        verbose_name_plural = 'Группы'
        ordering = ('title',)

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField('Текст поста',
                            help_text='Введите текст поста')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Автор')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              related_name='posts',
                              blank=True, null=True,
                              verbose_name='Группа',
                              help_text=' Выберите группу')
    image = models.ImageField('Картинка',
                              upload_to='posts/',
                              blank=True,
                              help_text='Картинка')

    class Meta:
        ordering = ['-pub_date', 'author']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(CreatedModel):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name='Текс поста',
                             blank=True,
                             null=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор')
    text = models.TextField(verbose_name='Комментарий',
                            help_text='Напишите комментарий')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    user = models.ForeignKey(User,
                             related_name='follower',
                             on_delete=models.CASCADE)
    author = models.ForeignKey(User,
                               related_name='following',
                               on_delete=models.CASCADE)

    class Meta:
        ordering = ('-author',)
        verbose_name = 'Лента автора'
        verbose_name_plural = 'Лента авторов'
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'], name='unique_members')]
