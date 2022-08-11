from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse

from ..models import Post


User = get_user_model()


class CacheTests(TestCase):
    """Cache tests."""
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Some text',
        )

    def test_cache_main(self):
        """Cache working test."""
        response = self.authorized_client.get(reverse('posts:index'))
        old_content = response.content
        Post.objects.all().delete()

        response = self.authorized_client.get(reverse('posts:index'))
        new_content = response.content
        self.assertEqual(old_content, new_content)

        """Content changing test."""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        new_content = response.content
        self.assertNotEqual(old_content, new_content)
