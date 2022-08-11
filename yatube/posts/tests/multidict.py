from django.urls import reverse
from http import HTTPStatus as HTTP


class MultyDict:
    """Class for containig 4 values, made for comfortable testing."""
    def __init__(
        self,
        guest_code=None,
        template='',
        url=None,
        reverse_name=None,
    ):
        self.guest_code = guest_code
        self.template = 'posts/{}.html'.format(template)
        self.url = url
        self.reverse_name = reverse_name


codes_data = (
    MultyDict(HTTP.OK, 'index', '/', reverse(
        'posts:index'
    )),
    MultyDict(HTTP.OK, 'group_list', '/group/test_slug/', reverse(
        'posts:group_list', kwargs={'slug': 'test_slug'}
    )),
    MultyDict(HTTP.OK, 'profile', '/profile/HasNoName/', reverse(
        'posts:profile', kwargs={'username': 'HasNoName'}
    )),
    MultyDict(HTTP.OK, 'post_detail', '/posts/1/', reverse(
        'posts:post_detail', kwargs={'post_id': 1}
    )),
    MultyDict(HTTP.FOUND, 'post_create', '/posts/1/edit/', reverse(
        'posts:post_edit', kwargs={'post_id': 1}
    )),
    MultyDict(HTTP.FOUND, 'post_create', '/create/', reverse(
        'posts:post_create'
    )),
    MultyDict(HTTP.NOT_FOUND, '', '/aba/', ),
)
templates_data = codes_data[:-1]
paginator_data = codes_data[:3]
