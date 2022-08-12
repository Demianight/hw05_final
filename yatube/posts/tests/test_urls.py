from http import HTTPStatus as HTTP

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User
from .multidict import codes_data, templates_data


class StaticURLTests(TestCase):
    """Urls tests"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.post = Post.objects.create(
            author=cls.user,
            text='Test text',
        )
        cls.group = Group.objects.create(
            title='TestGroup',
            slug='test_slug',
            description='Test description'
        )
        cls.edit_url = reverse('posts:post_edit', kwargs={
            'post_id': 1
        })

    def setUp(self) -> None:
        super().setUp()
        cache.clear()

    def test_guest_pages(self):
        """Test response codes for guest client."""
        for dict in codes_data:
            with self.subTest(url=dict.url):
                response = self.guest_client.get(dict.url)
                self.assertEqual(response.status_code, dict.guest_code)

    def test_templates(self):
        """Test for correct templates on pages."""
        for dict in templates_data:
            with self.subTest(template=dict.template):
                response = self.authorized_client.get(dict.url)
                self.assertTemplateUsed(response, dict.template)
                self.assertEqual(response.status_code, HTTP.OK)

    def test_edit_redirect(self):
        """Non-author client redirects from editing page."""
        non_author_client = Client()
        second_user = User.objects.create_user(username='NonAuthor')
        non_author_client.force_login(second_user)
        response = non_author_client.get(self.edit_url)
        self.assertRedirects(response, '/posts/1/')

    def test_guest_redirects(self):
        """Guest client redirects test."""
        guest_redirects = {
            self.edit_url: '/auth/login/?next={}',
            '/create/': '/auth/login/?next={}'
        }

        for url, redirect in guest_redirects.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, redirect.format(url))
