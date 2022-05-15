import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from ..models import Group, Post, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    """Протестируем, что добавляется новый пользователь."""

    test_data = {
        'user_username': 'auth',
        'group_title': 'Тестовая группа',
        'group_slug': 'test_slug',
        'group_description': 'Тестовое описание',
        'post_text': 'Тестовый пост',
        'username_author': 'author',
        'text': 'text',
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username=PostFormTest.test_data['user_username']
        )

        cls.group = Group.objects.create(
            title=PostFormTest.test_data['group_title'],
            slug=PostFormTest.test_data['group_slug'],
            description=PostFormTest.test_data['group_description'],
        )

        cls.post = Post.objects.create(
            author=User.objects.create_user(
                username=PostFormTest.test_data['username_author']
            ),
            group=cls.group,
            text=PostFormTest.test_data['text'],
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'test-text add',
            'group': '1',
            'author': PostFormTest.user,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertRedirects(
            response, reverse(
                'posts:profile',
                kwargs={'username': PostFormTest.test_data['user_username']}
            )
        )
        print(Post.objects.count())
        print(Group.objects.count())

    def test_comment_create(self):
        kw = {'post_id': self.post.id}
        response = self.client.get(
            reverse('posts:add_comment', kwargs=kw)
        )
        print(response)
        self.assertRedirects(
            response,
            f'{reverse("users:login")}'
            f'?next={reverse("posts:add_comment", kwargs=kw)}'
        )

    def test_comment_add(self):
        comment_count = Comment.objects.count()
        new_comment = {
            'text': 'text',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', args=[self.post.id]),
            data=new_comment,
            follow=True,
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_image(self):
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'test text',
            'group': '1',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ),
        )

        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='test text',
                group=self.group,
                image='posts/small.gif'
            ).exists()
        )
