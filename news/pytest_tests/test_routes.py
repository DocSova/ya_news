import pytest
from http import HTTPStatus

from django.urls import reverse


@pytest.mark.django_db
def test_pages_availability(client, news):
    urls = [
        ('news:home', None),
        ('news:detail', (news.id,)),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ]
    for name, args in urls:
        url = reverse(name, args=args)
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_availability_for_comment_edit_and_delete(
        admin_client, comment, author_client):
    users_statuses = [
        (author_client, HTTPStatus.OK),
        (admin_client, HTTPStatus.NOT_FOUND),
    ]
    for user, status in users_statuses:
        for name in ('news:edit', 'news:delete'):
            url = reverse(name, args=(comment.id,))
            response = user.get(url)
            assert response.status_code == status


@pytest.mark.django_db
def test_redirect_for_anonymous_client(client, comment):
    login_url = reverse('users:login')
    for name in ('news:edit', 'news:delete'):
        url = reverse(name, args=(comment.id,))
        redirect_url = f'{login_url}?next={url}'
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == redirect_url
