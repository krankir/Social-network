import shutil
import tempfile

from http import HTTPStatus
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Post, Group, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):

    def setUp(self):
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(name='small.gif',
                                           content=self.small_gif,
                                           content_type='image/gif')
        self.guest_client = Client()
        self.user = User.objects.create(username='Adam')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            id=1,
            title='Тестовая группа',
            slug='slug_group_1',
            description='Тестовая группа 1'
        )
        self.group2 = Group.objects.create(
            id=2,
            title='Тестовая группа №2',
            slug='test-group_2',
            description='Тестовая группа 2',
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовая, пост какойто',
            group=self.group,
            image=self.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_valid_form(self):
        """Проверка создания поста."""
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(name='small.gif',
                                           content=self.small_gif,
                                           content_type='image/gif')
        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.pk,
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        new_posts_count = Post.objects.count()
        post = Post.objects.last()

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(posts_count, new_posts_count)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.group)

    def test_can_edit_post(self):
        """Проверка  редактирования поста."""
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group2.id}
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(self.post.text, form_data['text'])


class CommentFormTest(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Adam')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test-group',
                                          description='Описание')
        self.post = Post.objects.create(text='Тестовый текст',
                                        author=self.user,
                                        group=self.group)
        self.comment = Comment.objects.create(post_id=self.post.id,
                                              author=self.user,
                                              text='Тестовый коммент')

    def test_create_comment(self):
        """Проверка создания комментария"""
        comment_count = Comment.objects.count()
        form_data = {'post_id': self.post.id,
                     'text': 'Тестовый коммент2'}
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Comment.objects.filter(
            text='Тестовый коммент2',
            post=self.post.id,
            author=self.user
        ).exists())
        self.assertEqual(Comment.objects.count(),
                         comment_count + 1)

    def test_edit_comment(self):
        """Проверка того что коментировать может только
           авторизованный пользователь"""
        posts_count = Comment.objects.count()
        form_data = {'text': 'Тестовый коммент2'}
        response = self.guest_client.post(reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(Comment.objects.count(),
                            posts_count + 1)
