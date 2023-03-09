from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from http import HTTPStatus

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        """Созданим запись в БД для проверки доступности
        адреса user/test-slug/"""
        cls.author = User.objects.create(username='TestAuthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый текст',
            group=cls.group
        )

    def setUp(self):
        # Создаем неавторизованого клиента
        self.guest_client = Client()
        # Создаем авторизованого клиента
        self.user = User.objects.create(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_guest_urls(self):
        """Проверяем общедоступные страницы"""
        urls_names = {
           '/': HTTPStatus.OK.value,
           '/group/test_slug/': HTTPStatus.OK.value,
           '/profile/TestAuthor/': HTTPStatus.OK.value,
           f'/posts/{self.post.pk}/': HTTPStatus.OK.value,
           '/unexisting_page/': HTTPStatus.NOT_FOUND.value,
        }
        for address, status in urls_names.items():
            with self.subTest(status=status):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status)

    def test_autorized_urls(self):
        """Проверяем страницы доступные автору поста"""
        urls_names = {
           f'/posts/{self.post.pk}/edit/': HTTPStatus.OK.value,
           '/create/': HTTPStatus.OK.value,
        }
        for address, status in urls_names.items():
            with self.subTest(status=status):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, status)
 