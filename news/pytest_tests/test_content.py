import pytest
from datetime import datetime, timedelta

from django.utils import timezone
from django.conf import settings
from django.urls import reverse

from news.models import Comment, News


@pytest.mark.django_db
def test_home_page_news_count(client):
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)

    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_home_page_news_order(client):
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)

    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_detail_page_comments_order(author_client, author, news):
    detail_url = reverse('news:detail', args=(news.id,))

    comments = []
    for index in range(2):
        created_date = timezone.now() + timedelta(days=index)
        comment = Comment.objects.create(
            news=news, author=author, text=f'Текст {index}',
            created=created_date
        )
        comments.append(comment)

    response = author_client.get(detail_url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
def test_detail_page_anonymous_client_has_no_form(client, news):
    detail_url = reverse('news:detail', args=(news.id,))
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_detail_page_authorized_client_has_form(author_client, news):
    detail_url = reverse('news:detail', args=(news.id,))
    response = author_client.get(detail_url)
    assert 'form' in response.context
