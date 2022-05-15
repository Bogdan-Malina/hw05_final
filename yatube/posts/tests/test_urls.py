from http import HTTPStatus

from django.test import TestCase, Client

from ..models import Group, Post, User


class StaticURLTests(TestCase):
    def test_homepage(self):
        guest_client = Client()
        response = guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostsURLTests(TestCase):
    test_data_group = {
        'title': 'Тестовая группа',
        'slug': 'test_slug',
    }

    test_data_post = {
        'username_author': 'test_username_2',
        'text': 'Тестовый пост',
    }

    test_data_users = {
        'username_author': 'test_username_2',
        'username': 'test_username',
    }

    urls = [
        '/',
        '/profile/test_username/',
        '/posts/1/',
        '/group/test_slug/',
    ]

    test_data = {
        '/': 'posts/index.html',
        '/create/': 'posts/create_post.html',
        '/profile/test_username/': 'posts/profile.html',
        '/posts/1/': 'posts/post_detail.html',
        '/group/test_slug/': 'posts/group_list.html',
        '/404': 'core/404.html',
    }

    test_data_status_auth = {
        '/create/': HTTPStatus.OK,
        '/unexisting_page/': HTTPStatus.NOT_FOUND,
        '/posts/1/edit/': HTTPStatus.OK,

    }

    test_data_guest = {
        '/create/': 'posts: post_create',
        '/posts/1/edit/': 'posts: post_edit'
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title=PostsURLTests.test_data_group['title'],
            slug=PostsURLTests.test_data_group['slug'],
        )
        cls.post = Post.objects.create(
            author=User.objects.create_user(
                username=PostsURLTests.test_data_post['username_author']
            ),
            text=PostsURLTests.test_data_post['text'],
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.user = User.objects.create_user(
            username=PostsURLTests.test_data_users['username']
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Создаем клиент автора
        self.user_2 = User.objects.get(
            username=PostsURLTests.test_data_users['username_author']
        )
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user_2)

    def test_urls_for_guest(self):
        """Тест HTTPStatus для guest_client"""
        for test_urls in PostsURLTests.urls:
            with self.subTest():
                response = self.guest_client.get(test_urls)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_for_auth(self):
        """Тест HTTPStatus для authorized_client"""
        for test_urls in PostsURLTests.urls:
            with self.subTest():
                response = self.authorized_client.get(test_urls)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_http_status_auth(self):
        """Тест HTTPStatus для authorized_client"""
        for url, status in PostsURLTests.test_data_status_auth.items():
            with self.subTest(url=url):
                response = self.authorized_client_author.get(url)
                self.assertEqual(response.status_code, status)

    def test_edit_redirect_not_author(self):
        """Тест redirect не автора поста с /posts/1/edit/ на страницу поста"""
        response = self.authorized_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, ('/posts/1/'))

    def test_unexisting_page_for_guest(self):
        """Тест HTTPStatus unexisting для guest_client"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_anonymous(self):
        """Тест redirect guest_client"""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

        for url, status in PostsURLTests.test_data_status_auth.items():
            with self.subTest(url=url):
                response = self.authorized_client_author.get(url)
                self.assertEqual(response.status_code, status)

    def test_templates(self):
        """Тест соответствия URL-адреса шаблону"""
        for test_urls, templates in PostsURLTests.test_data.items():
            with self.subTest(test_url=test_urls):
                response = self.authorized_client.get(test_urls)
                self.assertTemplateUsed(response, templates)
        response = self.authorized_client_author.get('/posts/1/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')
