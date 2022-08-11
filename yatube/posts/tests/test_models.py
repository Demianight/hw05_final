from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    """Models tests."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестировочный текст превышающий 15 символов',
        )

    def test_models_have_correct_object_names(self):
        """Test __str__ method in models."""
        names = {
            self.post: 'Тестировочный т',
            self.group: 'Тестовая группа',
        }
        for model, name in names.items():
            with self.subTest(model=model):
                self.assertEqual(str(model), name)
