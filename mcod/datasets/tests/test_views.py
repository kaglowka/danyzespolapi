import pytest
from falcon import HTTP_OK
from mcod.datasets.models import Dataset, FREQUENCY
from mcod.lib.tests.helpers.elasticsearch import ElasticCleanHelper


@pytest.mark.django_db
class TestDatasetsView(ElasticCleanHelper):
    def test_update_frequency_translations(self, client, valid_organization):
        # MCOD-1031
        for uf_code, readable in FREQUENCY:
            ds = Dataset(
                slug=f"test-{uf_code}-dataset",
                title=f"{readable} test name",
                organization=valid_organization,
                update_frequency=uf_code
            )
            ds.save()

            resp = client.simulate_get(f'/datasets/{ds.id}')
            assert HTTP_OK == resp.status
            body = resp.json
            assert readable == body['data']['attributes']['update_frequency']
