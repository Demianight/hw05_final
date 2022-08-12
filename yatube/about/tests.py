from http import HTTPStatus

from django.test import Client, TestCase


class URLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_author_url(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech_url(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
