import pytest
from django.core.exceptions import ValidationError

from mcod.categories.models import Category


@pytest.mark.django_db
class TestCategoryModel:

    def test_create_category(self):
        category = Category()
        category.slug = "category-slug"
        category.title = "Title"
        category.description = "Opis"
        assert category.full_clean() is None
        assert category.id is None
        category.save()
        assert category.id is not None
        assert Category.objects.last().slug == category.slug

    def test_category_name_uniqnes(self, valid_category):
        category = Category()
        category.slug = valid_category.slug
        with pytest.raises(ValidationError) as e:
            category.full_clean()
        assert "'slug':" in str(e.value)

    def test_category_str(self, valid_category):
        assert str(valid_category) == valid_category.slug
