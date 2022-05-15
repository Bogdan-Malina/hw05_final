from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        user_username = 'auth'

        group_title = 'Тестовая группа'
        group_slug = 'Тестовый слаг'
        group_description = 'Тестовое описание'

        post_text = 'x' * 20

        cls.test_data_group = {
            'title': 'Заголовок',
            'slug': 'ID группы',
            'description': 'Описание группы',
        }
        cls.test_data_post_verbose = {
            'text': 'Текcт поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        cls.test_data_post_help_text = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }

        super().setUpClass()
        cls.user = User.objects.create_user(username=user_username)
        cls.group = Group.objects.create(
            title=group_title,
            slug=group_slug,
            description=group_description,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=post_text,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = PostModelTest.group
        post = PostModelTest.post
        test_data = {
            group.title: group,
            post.text[:15]: post,
        }
        for expect, model in test_data.items():
            with self.subTest(field=expect):
                self.assertEqual(str(model), expect)

    def test_verbose_name(self):
        """Проверяем verbose_name"""
        group = PostModelTest.group
        post = PostModelTest.post

        def test_verbose(data, model):
            for field, expect in data.items():
                with self.subTest(field=field):
                    response = model._meta.get_field(field).verbose_name
                    self.assertEqual(response, expect)

        test_verbose(PostModelTest.test_data_group, group)
        test_verbose(PostModelTest.test_data_post_verbose, post)

    def test_help_text(self):
        """Проверяем help_text """
        post = PostModelTest.post

        for field, expect in PostModelTest.test_data_post_help_text.items():
            with self.subTest(field=field):
                response = post._meta.get_field(field).help_text
                self.assertEqual(response, expect)
