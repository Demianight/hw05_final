from django.test import TestCase, Client
from django.urls import reverse
from django.core.paginator import Page
from django.core.cache import cache
from time import sleep


from .multidict import paginator_data, templates_data
from ..forms import PostForm
from ..views import POSTS_ON_PAGE
from ..models import Post, Group, User


class ViewsTest(TestCase):
    """Different views functions tests."""
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Test Group',
            slug='test_slug'
        )
        cls.page_count = 12
        for i in range(cls.page_count):
            Post.objects.create(
                text='Test' * (i + 1),
                author=cls.user,
                group=cls.group
            )
            sleep(0.001)

        cls.post = Post.objects.create(
            text='Test1',
            author=cls.user,
            group=cls.group
        )

        cls.default_post_id = 1

    def setUp(self) -> None:
        super().setUp()
        cache.clear()

    def get_post(self, response):
        """This function checks for test post in different pages."""
        try:
            post = response.context['post']
        except KeyError:
            post = response.context['page_obj'][0]

        self.assertEqual(self.post, post)
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.group, self.group)

    def test_first_page_contains_ten_records(self):
        """Check for ten posts on pages with paginator."""
        for dict in paginator_data:
            with self.subTest(reverse_name=dict.reverse_name):
                response = self.authorized_client.get(dict.reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']), POSTS_ON_PAGE
                )

    def test_second_page_contains_three_records(self):
        """Check for three posts on second page with paginator."""
        for dict in paginator_data:
            with self.subTest(reverse_name=dict.reverse_name):
                response = self.authorized_client.get(
                    dict.reverse_name + '?page=2'
                )
                self.assertEqual(len(response.context['page_obj']), 3)

    def test_templates(self):
        """Test used templates for pages."""
        for dict in templates_data:
            with self.subTest(reverse_name=dict.reverse_name):
                response = self.authorized_client.get(dict.reverse_name)
                self.assertTemplateUsed(response, dict.template)

    def test_context_index(self):
        """Index page context test."""
        response = self.client.get(
            reverse(
                'posts:index'
            )
        )
        page_obj = response.context['page_obj']
        self.get_post(response)
        self.assertIsInstance(page_obj, Page)

    def test_context_group(self):
        """Group page context test"""
        response = self.client.get(
            reverse(
                'posts:group_list',
                kwargs={
                    'slug': self.group.slug
                }
            )
        )
        self.get_post(response)

    def test_context_profile(self):
        """Profile page context test."""
        response = self.client.get(
            reverse(
                'posts:profile',
                kwargs={
                    'username': self.user.username
                }
            )
        )
        self.get_post(response)

    def test_context_post_detail(self):
        """Post detail page context test."""
        response = self.client.get(
            reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': self.post.id
                }
            )
        )
        self.get_post(response)

    def test_context_create_post(self):
        """Create page context test."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_create'
            )
        )
        form = response.context['form']
        self.assertIsInstance(form, PostForm)

        is_edit = response.context['is_edit']
        self.assertEqual(is_edit, False)

    def test_context_edit_post(self):
        """Edit page context test."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': self.default_post_id
                }
            )
        )
        form = response.context['form']
        self.assertIsInstance(form, PostForm)
        self.assertEqual(form.instance.id, self.default_post_id)

        is_edit = response.context['is_edit']
        self.assertEqual(is_edit, True)

    def test_post_create(self):
        """Post appears on some pages test."""
        post = Post.objects.create(
            text='Something',
            author=self.user,
            group=self.group
        )

        success_urls = (
            reverse('posts:index'),
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        for url in success_urls:
            response = self.authorized_client.get(url)
            post = response.context['page_obj'][0]
            with self.subTest(url=url):
                self.assertEqual(post.id, post.id)

    def test_negative_options(self):
        """"Post didn't appear on unrelated pages."""
        user = User.objects.create(username='Negative')
        negative_group = Group.objects.create(
            title='Negative',
            slug='Negative',
        )
        negative_post = Post.objects.create(
            text='Negative',
            author=user,
            group=negative_group,
        )
        # Test for second pages
        negative_urls = (
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        for url in negative_urls:
            response = self.client.get(url)
            page_obj = response.context['page_obj']
            with self.subTest(url=url):
                self.assertNotIn(negative_post, page_obj)
