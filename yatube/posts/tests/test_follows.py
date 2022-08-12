from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Post, User


class FollowsTests(TestCase):
    """Basic follow tests."""
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.username = 'SecondUser'
        cls.user = User.objects.create(username='HasNoName')
        cls.another_user = User.objects.create(username=cls.username)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.post = Post.objects.create(
            author=cls.another_user,
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
                author=self.another_user.id,
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
                author=self.another_user.id,
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
