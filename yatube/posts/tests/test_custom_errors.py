from django.test import Client, TestCase


class ErrorPagesTessts(TestCase):
    def setUp(self):
        self.client = Client()

    def test_templates_names(self):
        response = self.client.get('/aba/')
        self.assertTemplateUsed(response, 'core/404.html')
