import time

from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post, User, Follow


class PostPagesTests(TestCase):
    test_data = {
        'user_username': 'test',
        'group_title': 'Тестовая группа',
        'group_slug': 'test_slug',
        'group_description': 'Тестовое описание',
        'post_text': 'Пост c группой №',
    }

    form_fields = {
        'text': forms.fields.CharField,
        'group': forms.fields.ChoiceField,
        'image': forms.fields.ImageField,
    }

    templates_pages_names = {
        'posts/index.html': reverse('posts:index'),
        'posts/group_list.html': reverse(
            'posts:group_list', kwargs={'slug': 'test_slug'}
        ),
        'posts/profile.html': reverse(
            'posts:profile', kwargs={'username': 'test'}
        ),
        'posts/post_detail.html': reverse(
            'posts:post_detail',
            kwargs={'post_id': '1'}
        ),
        'posts/create_post.html': reverse('posts:post_create'),
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username=PostPagesTests.test_data['user_username']
        )
        cls.group = Group.objects.create(
            title=PostPagesTests.test_data['group_title'],
            slug=PostPagesTests.test_data['group_slug'],
            description=PostPagesTests.test_data['group_description'],
        )

        cls.cache = cache

        for i in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                text=PostPagesTests.test_data['post_text'] + str(i),
                group=cls.group,
            )
            time.sleep(0.001)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        for template, reverse_name in \
                PostPagesTests.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Пост c группой №12')

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'posts:group_list', kwargs={
                    'slug': 'test_slug'}))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.group.slug, 'test_slug')
        self.assertEqual(first_object.text, 'Пост c группой №12')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'posts:profile', kwargs={
                    'username': 'test'}))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author.username, 'test')
        self.assertEqual(first_object.text, 'Пост c группой №12')

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': '1'}))
        self.assertEqual(response.context.get('post').author, self.user)
        self.assertEqual(
            response.context.get('post').text,
            'Пост c группой №0')
        self.assertEqual(response.context.get('post').group, self.group)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))

        get_object_or_404(Post, id=1)
        for value, expected in PostPagesTests.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_show_correct_context(self):
        """Шаблон edit_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 1})
        )
        get_object_or_404(Post, id=1)
        for value, expected in PostPagesTests.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_cache(self):
        self.cache.clear()
        post = Post.objects.create(
            author=self.user,
            text='test'
        )
        response = self.authorized_client.get(
            PostPagesTests.templates_pages_names['posts/index.html']
        )
        cache_post = response.content
        post.delete()
        response = self.authorized_client.get(
            PostPagesTests.templates_pages_names['posts/index.html']
        )
        self.assertEqual(response.content, cache_post)
        self.cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, cache_post)

    def test_follow(self):
        self.authorized_client.post(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user.username})
        )
        self.assertEqual(Follow.objects.count(), 0)

    def test_anon_comment_create(self):
        response = self.guest_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        test = '/auth/login/?next=/posts/13/edit/'
        self.assertRedirects(response, test)


class PaginatorTests(TestCase):
    POST_IN_PAGE_1 = 10
    POST_IN_PAGE_2 = 3

    test_data = {
        'user_username': 'test',
        'group_title': 'Тестовая группа',
        'group_slug': 'test_slug',
        'group_description': 'Тестовое описание',
        'post_text': 'Пост c группой №',
    }

    paginator_test = [
        reverse('posts:index'),
        reverse('posts:group_list', kwargs={'slug': test_data['group_slug']}),
        reverse(
            'posts:profile',
            kwargs={'username': test_data['user_username']}
        ),
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username=PaginatorTests.test_data['user_username']
        )
        cls.group = Group.objects.create(
            title=PaginatorTests.test_data['group_title'],
            slug=PaginatorTests.test_data['group_slug'],
            description=PaginatorTests.test_data['group_description'],
        )

        for i in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                text=PaginatorTests.test_data['post_text'] + str(i),
                group=cls.group,
            )
            time.sleep(0.001)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator(self):
        """Тест пагинатора"""
        for test in PaginatorTests.paginator_test:
            with self.subTest(test=test):
                response_1 = self.client.get(test)
                response_2 = self.client.get(test + '?page=2')
                self.assertEqual(
                    len(response_1.context['page_obj']),
                    PaginatorTests.POST_IN_PAGE_1
                )
                self.assertEqual(
                    len(response_2.context['page_obj']),
                    PaginatorTests.POST_IN_PAGE_2
                )
