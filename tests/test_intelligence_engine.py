from models.advertisement import Advertisement
from models.creative import CreativeFeatures
from pipeline.intelligence_engine import IntelligenceEngine


def make_ad(source_id: str, views: int, likes: int, comments: int, shares: int):
    return Advertisement(
        source_id=source_id,
        provider="sample",
        play_count=views,
        likes=likes,
        comments=comments,
        shares=shares,
        is_active=True,
        video_url="https://example.com/video.mp4",
    )


def make_feature(ad_id: str):
    return CreativeFeatures(
        ad_id=ad_id,
        provider="sample",
        detected_brand="Example",
        opening_style="Product first",
        creative_format="Video",
        visual_style="UGC",
        product_first=True,
        fast_edits=True,
        cta="Shop now",
        emotions=["Joy"],
        positioning=["Lifestyle"],
        proof_points=["Visible demonstration"],
        benefits=["Refreshing taste"],
        confidence=0.8,
    )


def test_intelligence_engine_returns_actionable_sections():
    ads = [
        make_ad("1", 10000, 400, 20, 10),
        make_ad("2", 8000, 250, 10, 5),
    ]
    features = [make_feature("1"), make_feature("2")]

    result = IntelligenceEngine().build(
        ads=ads,
        features=features,
        duplicate_rate=25,
        recommendations=["Test a story-led opening."],
        creative_brief={"Concept": "Summer starts here", "CTA": "Try it today"},
    )

    assert result["engagement"]["metrics"]
    assert result["creative"]["dimensions"]
    assert result["strategy"]["opportunities"]
    assert result["next_best_creative"]["confidence"] > 0
    assert result["next_best_creative"]["tests"]
