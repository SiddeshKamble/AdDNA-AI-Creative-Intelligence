from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from models.advertisement import Advertisement
from models.creative import CreativeFeatures
from models.market import MarketQuery
from models.report import MarketReport
from pipeline.ai_insights import AIInsightGenerator
from pipeline.creative_brief import CreativeBriefGenerator
from pipeline.pattern_engine import PatternEngine
from pipeline.intelligence_engine import IntelligenceEngine
from pipeline.recommendations import RecommendationEngine


class ReportGenerator:
    def __init__(self) -> None:
        self.pattern_engine = PatternEngine()
        self.recommendation_engine = RecommendationEngine()
        self.brief_generator = CreativeBriefGenerator()
        self.ai_insights = AIInsightGenerator()
        self.intelligence_engine = IntelligenceEngine()

    @staticmethod
    def _fallback_metric_insights(
        collected_count: int,
        unique_count: int,
        duplicate_rate: int,
        video_count: int,
        active_count: int,
        total_views: int,
    ) -> dict[str, str]:
        return {
            "Collected": (
                f"The analysis covers {collected_count} provider records; conclusions become stronger as the sample grows."
            ),
            "Unique": (
                f"{unique_count} distinct creatives remain after duplicate placements are removed."
            ),
            "Duplicate rate": (
                f"{duplicate_rate}% of collected records repeat existing creative, indicating placement concentration."
            ),
            "Video ads": (
                f"{video_count} unique creatives include a mapped video asset in the provider data."
            ),
            "Active ads": (
                f"{active_count} unique creatives are currently marked active, indicating recent market activity."
            ),
            "Total views": (
                f"{total_views:,} combined views are available; treat this as directional because provider coverage varies."
            ),
        }

    def generate(
        self,
        query: MarketQuery,
        collected_ads: list[Advertisement],
        unique_ads: list[Advertisement],
        duplicate_count: int,
        features: list[CreativeFeatures],
    ) -> MarketReport:
        patterns = self.pattern_engine.build(features)
        rule_opportunities, rule_recommendations = self.recommendation_engine.generate(
            features,
            patterns["pattern_presence"],
        )

        provider_counts = Counter(ad.provider for ad in unique_ads)
        platform_counts = Counter(
            platform
            for ad in unique_ads
            for platform in ad.platforms
        )
        detected_brands = Counter(
            ad.brand
            for ad in unique_ads
            if ad.brand and ad.brand != "Unknown"
        )
        top_brand = (
            detected_brands.most_common(1)[0][0]
            if detected_brands
            else "the detected advertisers"
        )
        dominant = patterns["creative_dna"]

        collected_count = len(collected_ads)
        unique_count = len(unique_ads)
        duplicate_rate = round(
            (duplicate_count / max(collected_count, 1)) * 100
        )
        video_count = sum(bool(ad.video_url) for ad in unique_ads)
        active_count = sum(ad.is_active is True for ad in unique_ads)
        total_views = sum(ad.play_count or 0 for ad in unique_ads)

        data_quality_notes: list[str] = []
        if query.brand and any(
            ad.brand.lower() != query.brand.lower()
            for ad in unique_ads
            if ad.brand != "Unknown"
        ):
            data_quality_notes.append(
                f"Some results mention '{query.brand}' but appear to come from other advertisers; provider brand labels were preserved."
            )
        if duplicate_count:
            data_quality_notes.append(
                f"Removed {duplicate_count} duplicate or near-duplicate placements before analysis."
            )
        if not any(ad.video_url for ad in unique_ads):
            data_quality_notes.append(
                "No mapped video URLs were available, so motion and edit-style conclusions are lower confidence."
            )
        if unique_count < 5:
            data_quality_notes.append(
                "The unique sample is small; treat all patterns as directional."
            )

        dominant_hook = dominant.get("Primary hook", "mixed openings")
        dominant_style = dominant.get("Visual style", "mixed styles")
        fallback_summary = (
            f"Across {unique_count} unique creatives, {dominant_hook.lower()} is the most common opening style, "
            f"while {dominant_style.lower()} is the dominant execution approach. "
            f"{top_brand} appears most often in the normalized sample. "
            f"The strongest directional whitespace is "
            f"{', '.join(rule_opportunities[:2]).lower() if rule_opportunities else 'greater hook, proof, and CTA differentiation'}."
        )

        fallback_metric_insights = self._fallback_metric_insights(
            collected_count=collected_count,
            unique_count=unique_count,
            duplicate_rate=duplicate_rate,
            video_count=video_count,
            active_count=active_count,
            total_views=total_views,
        )

        ai_output = self.ai_insights.generate(
            query=query,
            features=features,
            metrics={
                "collected_count": collected_count,
                "unique_count": unique_count,
                "duplicate_count": duplicate_count,
                "duplicate_rate": duplicate_rate,
                "video_count": video_count,
                "active_count": active_count,
                "total_views": total_views,
            },
            patterns=patterns,
            fallback={
                "executive_summary": fallback_summary,
                "metric_insights": fallback_metric_insights,
                "opportunity_gaps": rule_opportunities,
                "recommendations": rule_recommendations,
            },
        )

        recommendations = ai_output["recommendations"]
        opportunities = ai_output["opportunity_gaps"]

        llm_brief = ai_output.get("creative_brief", {})
        brief = (
            llm_brief
            if isinstance(llm_brief, dict) and llm_brief
            else self.brief_generator.generate(features, recommendations)
        )

        intelligence = self.intelligence_engine.build(
            ads=unique_ads,
            features=features,
            duplicate_rate=duplicate_rate,
            recommendations=recommendations,
            creative_brief=brief,
        )
        intelligence["market_ai"] = ai_output.get("market_intelligence", {})
        intelligence["ai_available"] = ai_output.get("ai_available", False)
        intelligence["ai_status"] = ai_output.get("ai_status", "")

        diversity = min(
            100,
            len(set(x for feature in features for x in feature.positioning)) * 18,
        )
        hook_strength = round(
            sum(feature.confidence for feature in features)
            / max(len(features), 1)
            * 100
        )
        cta_diversity = min(
            100,
            len(set(feature.cta for feature in features if feature.cta)) * 20,
        )
        visual_variety = min(
            100,
            len(set(feature.visual_style for feature in features)) * 35,
        )
        saturation = min(100, duplicate_rate + 45)
        whitespace = max(
            0,
            100 - round((diversity + cta_diversity + visual_variety) / 3),
        )

        return MarketReport(
            query=query.model_dump(mode="json"),
            generated_at=datetime.now(timezone.utc).isoformat(),
            collected_count=collected_count,
            unique_count=unique_count,
            duplicate_count=duplicate_count,
            duplicate_rate=duplicate_rate,
            provider_counts=dict(provider_counts),
            platform_counts=dict(platform_counts),
            active_count=active_count,
            video_count=video_count,
            total_views=total_views,
            data_quality_notes=data_quality_notes,
            executive_summary=ai_output["executive_summary"],
            metric_insights=ai_output["metric_insights"],
            intelligence=intelligence,
            winning_patterns=patterns["winning_patterns"],
            opportunity_gaps=opportunities,
            top_hooks=patterns["top_hooks"],
            messaging_breakdown=patterns["messaging_breakdown"],
            creative_dna=patterns["creative_dna"],
            market_scorecard={
                "Creative saturation": saturation,
                "Messaging diversity": diversity,
                "Visual variety": visual_variety,
                "Hook strength": hook_strength,
                "CTA diversity": cta_diversity,
                "Whitespace opportunity": whitespace,
            },
            recommendations=recommendations,
            creative_brief=brief,
            script=self.brief_generator.script(brief),
            shot_list=self.brief_generator.shot_list(brief),
            ads=unique_ads,
            features=features,
        )
