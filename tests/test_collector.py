from models.market import AdProvider, MarketQuery
from pipeline.collector import AdCollector


def test_sample_collection():
    ads = AdCollector().collect(
        MarketQuery(provider=AdProvider.SAMPLE, page_size=5)
    )
    assert len(ads) == 5
    assert all(ad.provider == "sample" for ad in ads)
