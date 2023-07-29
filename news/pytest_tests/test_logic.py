import pytest
from http import HTTPStatus

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data_comment, news):
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data_comment)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(
        author_client,
        author,
        news,
        form_data_comment):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data_comment)
    assert response.status_code == HTTPStatus.FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == 'Текст комментария'
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    form_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=form_data)
    assert response.context['form'].errors['text'][0] == WARNING
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(url)
    assert response.status_code == HTTPStatus.FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
        admin_client,
        comment):
    url = reverse('news:delete', args=(comment.id,))
    response = admin_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can_edit_comment(
        author_client,
        comment):
    edit_url = reverse('news:edit', args=(comment.id,))
    form_data = {'text': 'Обновлённый комментарий'}
    response = author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == 'Обновлённый комментарий'


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
        admin_client,
        comment):
    edit_url = reverse('news:edit', args=(comment.id,))
    form_data = {'text': 'Обновлённый комментарий'}
    response = admin_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'
