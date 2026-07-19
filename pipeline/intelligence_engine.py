from __future__ import annotations

from collections import Counter
from math import log10
from statistics import mean
from typing import Any, Optional
from models.advertisement import Advertisement
from models.creative import CreativeFeatures

class IntelligenceEngine:
    # Turn normalized creative and engagement evidence into decision-ready intelligence.
    @staticmethod
    def _pct(value: int, total: int) -> int:
        return round((value / max(total, 1)) * 100)

    @staticmethod
    def _level(score: int) -> str:
        if score >= 85:
            return "Excellent"
        if score >= 70:
            return "Strong"
        if score >= 55:
            return "Moderate"
        if score >= 40:
            return "Weak"
        return "Very weak"

    @staticmethod
    def _opportunity_level(score: int) -> str:
        if score >= 85:
            return "Very high"
        if score >= 70:
            return "High"
        if score >= 50:
            return "Medium"
        return "Low"

    @staticmethod
    def _engagement_rate(ad: Advertisement) -> Optional[float]:
        denominator = ad.impressions or ad.play_count
        if not denominator:
            return None

        weighted_interactions = (
            (ad.likes or 0)
            + ((ad.comments or 0) * 2)
            + ((ad.shares or 0) * 3)
        )
        return (weighted_interactions / denominator) * 100

    @staticmethod
    def _available_count(values: list[Any]) -> int:
        return sum(value is not None for value in values)

    def _metric(
        self,
        *,
        label: str,
        value: str,
        score: int,
        insight: str,
        improvement: str,
        confidence: str = "Directional",
    ) -> dict[str, Any]:
        return {
            "label": label,
            "value": value,
            "score": max(0, min(100, score)),
            "level": self._level(score),
            "insight": insight,
            "improvement": improvement,
            "confidence": confidence,
        }

    def engagement_intelligence(
        self,
        ads: list[Advertisement],
        features: list[CreativeFeatures],
        duplicate_rate: int,
    ) -> dict[str, Any]:
        rates = [
            rate
            for rate in (self._engagement_rate(ad) for ad in ads)
            if rate is not None
        ]
        total_views = sum(ad.play_count or 0 for ad in ads)
        total_interactions = sum(
            (ad.likes or 0) + (ad.comments or 0) + (ad.shares or 0)
            for ad in ads
        )
        avg_rate = mean(rates) if rates else 0.0
        active_share = self._pct(sum(ad.is_active is True for ad in ads), len(ads))
        video_share = self._pct(sum(bool(ad.video_url) for ad in ads), len(ads))
        product_first_share = self._pct(
            sum(feature.product_first for feature in features),
            len(features),
        )
        fast_edit_share = self._pct(
            sum(feature.fast_edits for feature in features),
            len(features),
        )
        cta_share = self._pct(
            sum(bool(feature.cta and feature.cta != "Unknown") for feature in features),
            len(features),
        )

        reach_score = min(100, round(log10(max(total_views, 1)) * 15))
        interaction_score = (
            min(100, round(avg_rate * 22))
            if rates
            else min(60, round(log10(max(total_interactions, 1)) * 15))
        )
        attention_score = round(
            product_first_share * 0.45
            + fast_edit_share * 0.35
            + video_share * 0.20
        )
        freshness_score = active_share
        fatigue_score = min(100, duplicate_rate + max(0, 60 - freshness_score) // 2)
        overall_score = round(
            reach_score * 0.25
            + interaction_score * 0.25
            + attention_score * 0.25
            + freshness_score * 0.15
            + (100 - fatigue_score) * 0.10
        )

        rate_confidence = (
            "High"
            if len(rates) >= max(5, len(ads) // 2)
            else "Directional"
        )

        metrics = [
            self._metric(
                label="Overall performance",
                value=f"{overall_score}/100",
                score=overall_score,
                insight=(
                    "The score combines available reach, interaction, attention signals, "
                    "active-ad share, and creative fatigue."
                ),
                improvement=(
                    "Prioritize the lowest-scoring component rather than increasing volume alone."
                ),
                confidence=rate_confidence,
            ),
            self._metric(
                label="Available engagement rate",
                value=f"{avg_rate:.2f}%" if rates else "Unavailable",
                score=interaction_score,
                insight=(
                    f"Engagement data was available for {len(rates)} of {len(ads)} unique creatives."
                    if rates
                    else "The providers did not return enough interaction data for a reliable rate."
                ),
                improvement=(
                    "Improve shareability with stronger emotional payoff, utility, or a comment-worthy prompt."
                ),
                confidence=rate_confidence,
            ),
            self._metric(
                label="Attention capture",
                value=f"{attention_score}/100",
                score=attention_score,
                insight=(
                    f"{product_first_share}% are product-first and {fast_edit_share}% use fast editing."
                ),
                improvement=(
                    "Test a stronger first-frame contrast, curiosity gap, or visible outcome in the opening seconds."
                ),
            ),
            self._metric(
                label="Active creative share",
                value=f"{active_share}%",
                score=active_share,
                insight=(
                    "A higher active share suggests the market is currently supporting these executions."
                ),
                improvement=(
                    "Separate currently active patterns from historical patterns before copying market conventions."
                ),
            ),
            self._metric(
                label="Creative fatigue risk",
                value=f"{fatigue_score}/100",
                score=100 - fatigue_score,
                insight=(
                    f"The duplicate rate is {duplicate_rate}%, which signals repeated placement or limited creative rotation."
                ),
                improvement=(
                    "Rotate hooks, opening visuals, creators, proof formats, and CTAs before only changing captions."
                ),
            ),
            self._metric(
                label="CTA coverage",
                value=f"{cta_share}%",
                score=cta_share,
                insight=(
                    f"{cta_share}% of analyzed creatives contain a detectable CTA."
                ),
                improvement=(
                    "Test earlier, clearer, benefit-led CTAs and make the next action visually unmistakable."
                ),
            ),
        ]

        strengths = []
        weaknesses = []
        if reach_score >= 70:
            strengths.append("Strong available reach across the unique sample.")
        else:
            weaknesses.append("Reach evidence is limited or concentrated in a small number of ads.")
        if attention_score >= 70:
            strengths.append("Openings use several established attention-capture signals.")
        else:
            weaknesses.append("Opening patterns may not create enough immediate contrast or curiosity.")
        if fatigue_score >= 55:
            weaknesses.append("Creative repetition creates a meaningful fatigue risk.")
        if cta_share < 65:
            weaknesses.append("CTA coverage is inconsistent.")
        if not weaknesses:
            weaknesses.append("No single severe weakness was detected; focus on differentiated testing.")

        return {
            "overall_score": overall_score,
            "overall_level": self._level(overall_score),
            "metrics": metrics,
            "strengths": strengths[:4],
            "weaknesses": weaknesses[:4],
        }

    def creative_intelligence(
        self,
        features: list[CreativeFeatures],
    ) -> dict[str, Any]:
        total = max(len(features), 1)
        opening_counts = Counter(feature.opening_style for feature in features)
        format_counts = Counter(feature.creative_format for feature in features)
        visual_counts = Counter(feature.visual_style for feature in features)
        emotion_counts = Counter(
            emotion
            for feature in features
            for emotion in feature.emotions
        )
        positioning_counts = Counter(
            item
            for feature in features
            for item in feature.positioning
        )

        comparison_share = self._pct(
            sum(feature.comparison_hook for feature in features), total
        )
        humor_share = self._pct(sum(feature.humor for feature in features), total)
        founder_share = self._pct(
            sum(feature.founder_led for feature in features), total
        )
        proof_share = self._pct(
            sum(bool(feature.proof_points) for feature in features), total
        )
        benefit_share = self._pct(
            sum(bool(feature.benefits) for feature in features), total
        )

        hook_diversity = min(100, len(opening_counts) * 18)
        visual_variety = min(100, (len(format_counts) + len(visual_counts)) * 10)
        emotion_depth = min(100, len(emotion_counts) * 16)
        positioning_diversity = min(100, len(positioning_counts) * 14)
        proof_score = proof_share
        creative_score = round(
            hook_diversity * 0.25
            + visual_variety * 0.25
            + emotion_depth * 0.15
            + positioning_diversity * 0.15
            + proof_score * 0.20
        )

        dominant_opening = opening_counts.most_common(1)[0][0] if opening_counts else "Unknown"
        dominant_format = format_counts.most_common(1)[0][0] if format_counts else "Unknown"
        dominant_visual = visual_counts.most_common(1)[0][0] if visual_counts else "Unknown"
        dominant_emotion = emotion_counts.most_common(1)[0][0] if emotion_counts else "Neutral"
        dominant_position = (
            positioning_counts.most_common(1)[0][0]
            if positioning_counts
            else "General"
        )

        dimensions = [
            self._metric(
                label="Hook intelligence",
                value=f"{hook_diversity}/100",
                score=hook_diversity,
                insight=f"The dominant opening is {dominant_opening}.",
                improvement=(
                    "Build a testing matrix across problem, question, story, comparison, offer, and outcome-led openings."
                ),
            ),
            self._metric(
                label="Visual intelligence",
                value=f"{visual_variety}/100",
                score=visual_variety,
                insight=(
                    f"{dominant_format} is the dominant format and {dominant_visual} is the leading visual style."
                ),
                improvement=(
                    "Change the visual mechanism—not just the copy—using creator, demo, animation, close-up, and lifestyle variants."
                ),
            ),
            self._metric(
                label="Emotional intelligence",
                value=f"{emotion_depth}/100",
                score=emotion_depth,
                insight=f"{dominant_emotion} is the most common detected emotion.",
                improvement=(
                    "Pair the product benefit with a stronger emotional payoff such as relief, joy, belonging, confidence, or humor."
                ),
            ),
            self._metric(
                label="Proof intelligence",
                value=f"{proof_score}/100",
                score=proof_score,
                insight=f"{proof_share}% of creatives contain a detectable proof point.",
                improvement=(
                    "Add demonstrations, quantified claims, testimonials, comparisons, or visible before-and-after evidence."
                ),
            ),
            self._metric(
                label="Positioning intelligence",
                value=f"{positioning_diversity}/100",
                score=positioning_diversity,
                insight=f"{dominant_position} is the leading positioning theme.",
                improvement=(
                    "Create a distinct position that competitors are not already repeating."
                ),
            ),
        ]

        return {
            "overall_score": creative_score,
            "overall_level": self._level(creative_score),
            "dimensions": dimensions,
            "signals": {
                "comparison_hook_share": comparison_share,
                "humor_share": humor_share,
                "founder_led_share": founder_share,
                "proof_share": proof_share,
                "benefit_share": benefit_share,
                "dominant_opening": dominant_opening,
                "dominant_format": dominant_format,
                "dominant_visual": dominant_visual,
                "dominant_emotion": dominant_emotion,
                "dominant_positioning": dominant_position,
            },
        }


    def market_intelligence(
        self,
        features: list[CreativeFeatures],
    ) -> dict[str, Any]:
        """Build concise, evidence-led market intelligence for the dashboard."""
        total = max(len(features), 1)

        def distribution(values: list[str], limit: int = 5) -> list[dict[str, Any]]:
            counts = Counter(value for value in values if value and value != "Unknown")
            return [
                {
                    "label": label,
                    "count": count,
                    "percentage": self._pct(count, total),
                }
                for label, count in counts.most_common(limit)
            ]
        formats = distribution(
            [feature.creative_format for feature in features],
            limit=5,
        )
        hooks = distribution(
            [feature.hook for feature in features if feature.hook],
            limit=5,
        )
        positioning = distribution(
            [
                item
                for feature in features
                for item in feature.positioning
            ],
            limit=5,
        )
        signals = {
            "Founder videos": self._pct(
                sum(feature.founder_led for feature in features),
                total,
            ),
            "Testimonials or proof": self._pct(
                sum(bool(feature.proof_points) for feature in features),
                total,
            ),
            "Product demos": self._pct(
                sum(
                    "demo" in feature.creative_format.lower()
                    or "product" in feature.creative_format.lower()
                    for feature in features
                ),
                total,
            ),
            "Humor": self._pct(
                sum(feature.humor for feature in features),
                total,
            ),
            "Interactive comparison": self._pct(
                sum(feature.comparison_hook for feature in features),
                total,
            ),
            "Behind the scenes": self._pct(
                sum(
                    "behind" in feature.visual_style.lower()
                    or "behind" in feature.creative_format.lower()
                    for feature in features
                ),
                total,
            ),
        }

        competitors_use = [
            {"label": label, "percentage": percentage}
            for label, percentage in signals.items()
            if percentage >= 15
        ]
        underused = [
            {"label": label, "percentage": percentage}
            for label, percentage in signals.items()
            if percentage < 15
        ]

        if not competitors_use:
            competitors_use = [
                {
                    "label": "Benefit-led messaging",
                    "percentage": self._pct(
                        sum(bool(feature.benefits) for feature in features),
                        total,
                    ),
                }
            ]

        return {
            "formats": formats,
            "hooks": hooks,
            "positioning": positioning,
            "creative_gaps": {
                "competitors_use": competitors_use[:4],
                "underused": underused[:4],
            },
        }

    def strategy_intelligence(
        self,
        features: list[CreativeFeatures],
        duplicate_rate: int,
    ) -> dict[str, Any]:
        total = max(len(features), 1)
        humor_share = self._pct(sum(feature.humor for feature in features), total)
        comparison_share = self._pct(
            sum(feature.comparison_hook for feature in features), total
        )
        founder_share = self._pct(
            sum(feature.founder_led for feature in features), total
        )
        proof_share = self._pct(
            sum(bool(feature.proof_points) for feature in features), total
        )
        emotion_variety = len(
            {
                emotion
                for feature in features
                for emotion in feature.emotions
            }
        )
        opening_variety = len({feature.opening_style for feature in features})
        visual_variety = len({feature.visual_style for feature in features})

        opportunities = [
            {
                "name": "Humor",
                "score": max(0, 100 - humor_share),
                "evidence": f"Only {humor_share}% of creatives use humor.",
                "action": "Test humor that reinforces the product truth rather than distracting from it.",
            },
            {
                "name": "Comparison",
                "score": max(0, 100 - comparison_share),
                "evidence": f"Only {comparison_share}% use a comparison hook.",
                "action": "Use a clear before/after, alternative comparison, or category contrast.",
            },
            {
                "name": "Founder or expert voice",
                "score": max(0, 100 - founder_share),
                "evidence": f"Only {founder_share}% use a founder-led approach.",
                "action": "Test a credible human explanation, expert POV, or behind-the-product story.",
            },
            {
                "name": "Proof-led creative",
                "score": max(0, 100 - proof_share),
                "evidence": f"{proof_share}% include a detectable proof point.",
                "action": "Make the claim visible through demonstration, data, testimonial, or result.",
            },
            {
                "name": "Emotional differentiation",
                "score": max(0, 100 - min(100, emotion_variety * 18)),
                "evidence": f"The sample uses {emotion_variety} distinct emotional territories.",
                "action": "Own an emotional territory that is uncommon in the current category.",
            },
            {
                "name": "Opening differentiation",
                "score": max(0, 100 - min(100, opening_variety * 17)),
                "evidence": f"The sample uses {opening_variety} distinct opening styles.",
                "action": "Test a deliberately contrasting opening rather than copying the category leader.",
            },
        ]
        opportunities = sorted(opportunities, key=lambda item: item["score"], reverse=True)
        average_opportunity = round(mean(item["score"] for item in opportunities))
        saturation = min(100, duplicate_rate + max(0, 55 - opening_variety * 7))
        market_opportunity = round(
            average_opportunity * 0.65 + (100 - saturation) * 0.35
        )

        for item in opportunities:
            item["level"] = self._opportunity_level(item["score"])

        return {
            "market_opportunity_score": market_opportunity,
            "market_opportunity_level": self._opportunity_level(market_opportunity),
            "market_saturation_score": saturation,
            "opportunities": opportunities[:6],
        }

    def next_best_creative(
        self,
        strategy: dict[str, Any],
        creative: dict[str, Any],
        recommendations: list[str],
        creative_brief: dict[str, Any],
    ) -> dict[str, Any]:
        top_opportunities = strategy.get("opportunities", [])[:3]
        opportunity_names = [item["name"] for item in top_opportunities]

        confidence = min(
            95,
            round(
                strategy.get("market_opportunity_score", 50) * 0.55
                + creative.get("overall_score", 50) * 0.25
                + 20
            ),
        )
        primary_opportunity = opportunity_names[0] if opportunity_names else "Creative differentiation"

        concept = (
            creative_brief.get("Concept")
            or creative_brief.get("concept")
            or f"{primary_opportunity} market test"
        )
        hook = (
            creative_brief.get("Opening")
            or creative_brief.get("opening")
            or f"Open with a {primary_opportunity.lower()}-led pattern interrupt."
        )
        cta = (
            creative_brief.get("CTA")
            or creative_brief.get("cta")
            or "Use a clear benefit-led CTA before the final five seconds."
        )

        return {
            "title": str(concept),
            "confidence": confidence,
            "expected_impact": self._opportunity_level(confidence),
            "primary_opportunity": primary_opportunity,
            "why": [
                item["evidence"]
                for item in top_opportunities
            ],
            "hook": str(hook),
            "cta": str(cta),
            "execution": (
                "Create a 20–30 second vertical concept with a distinct first-frame pattern, "
                "visible proof, emotional payoff, and an early CTA."
            ),
            "tests": recommendations[:3],
        }

    def build(
        self,
        ads: list[Advertisement],
        features: list[CreativeFeatures],
        duplicate_rate: int,
        recommendations: list[str],
        creative_brief: dict[str, Any],
    ) -> dict[str, Any]:
        engagement = self.engagement_intelligence(ads, features, duplicate_rate)
        creative = self.creative_intelligence(features)
        market = self.market_intelligence(features)
        strategy = self.strategy_intelligence(features, duplicate_rate)
        next_creative = self.next_best_creative(
            strategy,
            creative,
            recommendations,
            creative_brief,
        )

        return {
            "engagement": engagement,
            "creative": creative,
            "market": market,
            "strategy": strategy,
            "next_best_creative": next_creative,
        }
