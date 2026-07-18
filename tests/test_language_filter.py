from models.advertisement import Advertisement
from pipeline.language_filter import AdLanguageFilter


def test_english_filter_keeps_english_and_removes_portuguese():
    ads = [
        Advertisement(
            source_id="en-1",
            provider="sample",
            title="Meet the drink that makes every meal better",
            ad_copy="Shop now and discover the refreshing taste you love.",
        ),
        Advertisement(
            source_id="pt-1",
            provider="sample",
            title="Pague menos",
            ad_copy="Leve sua garrafa retornável e economize agora.",
            language="pt",
        ),
    ]
    result = AdLanguageFilter().apply(
        ads,
        english_only=True,
        minimum_confidence=0.5,
    )
    assert [ad.source_id for ad in result.kept_ads] == ["en-1"]
    assert result.removed_count == 1
