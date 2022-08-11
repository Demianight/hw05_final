from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from ..models import Post, Follow

User = get_user_model()


class FollowsTests(TestCase):
    """Basic follow tests."""
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.username = 'SecondUser'
        cls.user = User.objects.create(username='HasNoName')
        cls.user_2 = User.objects.create(username=cls.username)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.post = Post.objects.create(
            author=cls.user_2,
            text='Test text',
        )

    def test_follow_and_unfollow(self):
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={
                    'username': self.username
                }
            )
        )
        self.assertTrue(
            Follow.objects.filter(
                author=self.user_2.id,
                user_id=self.user.id
            ).exists()
        )

        # Unfollow test
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={
                    'username': self.username
                }
            )
        )
        self.assertFalse(
            Follow.objects.filter(
                author=self.user_2.id,
                user_id=self.user.id
            ).exists()
        )

    def test_index_follow(self):
        """"""
        # Followed user have post on follow page
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={
                    'username': self.username
                }
            )
        )
        response = self.authorized_client.get(
            reverse(
                'posts:follow_index',
            )
        )
        post = response.context['page_obj'][0]
        self.assertEqual(post, self.post)

        # Unfollowed user don't have post on follow page
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={
                    'username': self.username
                }
            )
        )
        response = self.authorized_client.get(
            reverse(
                'posts:follow_index',
            )
        )
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj), 0)
