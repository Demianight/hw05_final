import tempfile
import shutil

from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.cache import cache

from posts.models import Post, Group
from posts.forms import PostForm


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


class PostFormTests(TestCase):
    """Tests for post creating form."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='HasNoName')
        cls.client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Test group',
            slug='test_slug',
        )

        cls.test_text = 'Test text'
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.gif = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text=cls.test_text,
            author=cls.user,
            group=cls.group,
        )

        cls.form = PostForm()
        cls.posts_count = Post.objects.count()

    def setUp(self) -> None:
        super().setUp()
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        """Deletes temporary file directory."""
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """New post appeared in table."""
        form_data = {
            'text': self.test_text,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={'username': self.user.username}
            )
        )
        self.assertEqual(Post.objects.count(), self.posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=self.test_text,
                author=self.user,
                group=None,
            ).exists()
        )

    def test_edit_form(self):
        """Test editing part of form."""
        url = reverse(
            'posts:post_edit', kwargs={'post_id': self.post.id}
        )
        self.authorized_client.post(url, {
            'text': 'NewText'
        })
        post = Post.objects.get(id=self.post.id)

        """Edit test"""
        self.assertEqual(post.text, 'NewText')

        """Posts amount didn't change"""
        self.assertEqual(self.posts_count, Post.objects.count())

    def test_form_post_image(self):
        """Post with image appeared in the table."""
        Post.objects.create(
            text='Test text 2',
            group=self.group,
            image=self.gif,
            author=self.user,
        )
        urls = (
            '/', '/group/test_slug/', '/profile/HasNoName/', '/posts/2/'
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                try:
                    post = response.context['post']
                except KeyError:
                    post = response.context['page_obj'][0]

                self.assertTrue(post.image)
