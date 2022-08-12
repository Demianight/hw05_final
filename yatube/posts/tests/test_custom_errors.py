from django.test import Client, TestCase


class ErrorPagesTessts(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.client = Client()

    def test_templates_names(self):
        response = self.client.get('/aba/')
        self.assertTemplateUsed(response, 'core/404.html')
