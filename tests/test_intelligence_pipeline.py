from models.advertisement import Advertisement
from models.market import AdProvider, MarketQuery
from pipeline.deduplicator import CreativeDeduplicator
from pipeline.feature_extractor import CreativeFeatureExtractor
from pipeline.orchestrator import AdDNAPipeline


def test_near_duplicate_copy_is_removed():
    ads = [
        Advertisement(source_id="1", provider="sample", ad_copy="Still struggling with knee pain? Get yours here."),
        Advertisement(source_id="2", provider="sample", ad_copy="Still struggling with knee pain? Get yours here!"),
    ]
    result = CreativeDeduplicator().deduplicate(ads)
    assert len(result.unique_ads) == 1
    assert result.duplicate_count == 1


def test_hook_and_cta_are_extracted():
    ad = Advertisement(
        source_id="1",
        provider="sample",
        ad_copy="Still struggling with knee pain? Recover faster. Get yours here.",
    )
    feature = CreativeFeatureExtractor().extract(ad)
    assert feature.hook.startswith("Still struggling")
    assert feature.cta == "Get Yours Here"
    assert "Knee discomfort" in feature.pain_points


def test_sample_pipeline_returns_full_report():
    query = MarketQuery(brand="Nike", category="Shoes", provider=AdProvider.SAMPLE, page_size=5)
    report = AdDNAPipeline().run(query)
    assert report["unique_count"] >= 1
    assert "executive_summary" in report
    assert "creative_brief" in report
    assert "script" in report
    assert "shot_list" in report
