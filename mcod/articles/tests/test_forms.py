import pytest
from mcod.articles.forms import ArticleForm
from mcod.articles.models import Article


@pytest.mark.django_db
class TestArticleFormValidity:
    def test_article_form_add_tag(self, valid_tag):
        form = ArticleForm(data={
            'title': "Article with tag",
            'slug': "article-with-tag",
            'app_url': "http://test.pl",
            'notes': 'tresc',
            'status': 'published',
            'tags': [valid_tag]
        })
        assert form.is_valid() is True
        form.save()
        assert valid_tag in Article.objects.last().tags.all()

    @pytest.mark.parametrize(
        'title, slug, notes, author, license_id, status, tag, validity',
        [
            # correct scenarios
            ("Article published", "slug", "content", None, None, "published", None, True),
            ("Article draft", "slug", "content", None, None, "draft", None, True),
            # incorrect scenarios
            (None, "withot-title", "content", None, None, "published", None, False),
            ("Without slug", None, None, None, None, "published", None, False),
            ("Without notes", "article-title", None, None, None, "published",  None, False),
            ("Wrong", "article", "status", None, None, "value", None, False),
            ("Wrong", "article", "author", "a" * 51, None, "length", None, False),
        ])
    def test_article_form_validity(self, title, slug, notes, author, license_id, status, tag, validity):
        form = ArticleForm(data={
            'title': title,
            'slug': slug,
            'notes': notes,
            'author': author,
            'license_id': license_id,
            'status': status,
            'tag': tag,
        })
        assert form.is_valid() is validity
        if validity:
            form.save()
            assert Article.objects.last().slug == slug
