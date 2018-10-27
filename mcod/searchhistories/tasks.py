from django.apps import apps

from celery import task


@task
def create_search_history(url, q, user_id):
    SearchHistory = apps.get_model('searchhistories', 'SearchHistory')
    User = apps.get_model('users', 'User')
    try:
        usr = User.objects.get(pk=user_id)

        SearchHistory.objects.create(
            url=url,
            query_sentence=q,
            user=usr
        )
        return {
            'user_id': user_id,
            'url': url
        }

    except User.DoesNotExist:
        return {}
