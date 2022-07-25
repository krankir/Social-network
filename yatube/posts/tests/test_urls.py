from django.contrib.auth import get_user_model
from http import HTTPStatus
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='Tima')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=PostURLTests.user,
            text='Тестовая пост',
            group=PostURLTests.group,
        )

    def setUp(self) -> None:
        super().setUp()
        self.unauthorized_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(PostURLTests.post.author)

    def test_public_urls_available(self):
        """Страницы доступны неавторизованному пользователю
           и соответствуют шаблонам"""
        public_urls = [
            ('/', 'posts/index.html'),
            (f'/group/{PostURLTests.group.slug}/', 'posts/group_list.html'),
            (f'/profile/{PostURLTests.user.username}/', 'posts/profile.html'),
            (f'/posts/{PostURLTests.post.pk}/', 'posts/post_detail.html'),
        ]

        for url, template in public_urls:
            with self.subTest(url=url):
                response = self.unauthorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_urls_authorized_client(self):
        """Страницы доступны авторизованному пользователю
           и соответствуют шаблонам"""
        authorized_pages = [
            ('/create/', 'posts/create_post.html'),
            (f'/posts/{PostURLTests.post.pk}/edit/', 'posts/create_post.html'),
        ]

        for url, template in authorized_pages:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page_url(self):
        """Страница /unexisting_page/ выдаёт ошибку 404."""
        response = self.unauthorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
