import pytest
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def form_data_news():
    return {
        'title': 'Новый заголовок',
        'text': 'Новый текст'
    }


@pytest.fixture
def form_data_comment():
    return {
        'text': 'Текст комментария'
    }


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def news():
    return News.objects.create(  # Создаём объект заметки.
        title='Новый заголовок',
        text='Новый текст',
        date=timezone.now()
    )
