from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from ..models import Post

User = get_user_model()


class CommentsTests(TestCase):
    """"Basic comments tests."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='HasNoName')
        cls.client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post: Post = Post.objects.create(
            author=cls.user,
            text='Test Text',
        )
        cls.new_text = 'New Comment'

    def test_guest_comment_fail(self):
        """Guest client post attempt failed."""
        self.client.post(
            f'/posts/{self.post.id}/comment/',
            data={
                'text': self.new_text
            }
        )
        self.assertEqual(len(self.post.comments.all()), 0)

    def test_comment_win(self):
        """Authorized client post attempt accepted."""
        self.authorized_client.post(
            f'/posts/{self.post.id}/comment/',
            data={
                'text': self.new_text,
            }
        )
        self.assertEqual(len(self.post.comments.all()), 1)

        """Comment appeared on the page"""
        response = self.client.get(f'/posts/{self.post.id}/')
        comment = response.context['comments'][0]
        self.assertEqual(comment.text, self.new_text)
