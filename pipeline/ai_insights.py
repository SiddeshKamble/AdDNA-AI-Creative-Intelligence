from __future__ import annotations

from collections import Counter
import json
from typing import Any, Dict, List

from core.settings import settings
from llm.openrouter import OpenRouterClient
from llm.parser import parse_json_content
from models.creative import CreativeFeatures
from models.market import MarketQuery


class AIInsightGenerator:
    # Generate evidence-grounded market intelligence through OpenRouter.
    def __init__(self) -> None:
        self.client = OpenRouterClient()

    @staticmethod
    def _feature_payload(
        features: List[CreativeFeatures],
    ) -> List[Dict[str, Any]]:
        return [
            {
                "ad_id": item.ad_id,
                "detected_brand": item.detected_brand,
                "platforms": item.platforms,
                "hook": item.hook,
                "cta": item.cta,
                "pain_points": item.pain_points,
                "benefits": item.benefits,
                "proof_points": item.proof_points,
                "audience": item.audience,
                "positioning": item.positioning,
                "emotions": item.emotions,
                "creative_format": item.creative_format,
                "opening_style": item.opening_style,
                "visual_style": item.visual_style,
                "tone": item.tone,
                "product_first": item.product_first,
                "founder_led": item.founder_led,
                "comparison_hook": item.comparison_hook,
                "humor": item.humor,
                "fast_edits": item.fast_edits,
                "confidence": item.confidence,
            }
            for item in features
        ]

    @staticmethod
    def _evidence_summary(
        features: List[CreativeFeatures],
    ) -> Dict[str, Any]:
        total = max(len(features), 1)

        def summarize(values: List[str], limit: int = 8) -> List[Dict[str, Any]]:
            counts = Counter(
                value for value in values
                if value and value != "Unknown"
            )
            return [
                {
                    "label": label,
                    "count": count,
                    "percentage": round((count / total) * 100),
                }
                for label, count in counts.most_common(limit)
            ]

        return {
            "sample_size": len(features),
            "formats": summarize(
                [item.creative_format for item in features]
            ),
            "opening_styles": summarize(
                [item.opening_style for item in features]
            ),
            "visual_styles": summarize(
                [item.visual_style for item in features]
            ),
            "hooks": summarize(
                [item.hook for item in features if item.hook]
            ),
            "ctas": summarize(
                [item.cta for item in features if item.cta]
            ),
            "positioning": summarize(
                [value for item in features for value in item.positioning]
            ),
            "audiences": summarize(
                [value for item in features for value in item.audience]
            ),
            "emotions": summarize(
                [value for item in features for value in item.emotions]
            ),
            "pain_points": summarize(
                [value for item in features for value in item.pain_points]
            ),
            "benefits": summarize(
                [value for item in features for value in item.benefits]
            ),
            "proof_usage": round(
                sum(bool(item.proof_points) for item in features)
                / total * 100
            ),
            "founder_led_usage": round(
                sum(item.founder_led for item in features)
                / total * 100
            ),
            "comparison_usage": round(
                sum(item.comparison_hook for item in features)
                / total * 100
            ),
            "humor_usage": round(
                sum(item.humor for item in features)
                / total * 100
            ),
            "product_first_usage": round(
                sum(item.product_first for item in features)
                / total * 100
            ),
            "fast_edit_usage": round(
                sum(item.fast_edits for item in features)
                / total * 100
            ),
        }

    @staticmethod
    def _fallback_brief(
        query: MarketQuery,
        fallback: Dict[str, Any],
    ) -> Dict[str, Any]:
        recommendations = fallback.get("recommendations", [])
        first_recommendation = (
            recommendations[0]
            if recommendations
            else "Test a differentiated hook and proof mechanism."
        )
        platforms = query.platforms or ["social"]
        return {
            "Objective": "Improve creative engagement with a differentiated market test.",
            "Audience": "The most relevant audience detected in the analyzed sample.",
            "Insight": "The market is relying on repeated conventions, leaving room for a clearer emotional and proof-led execution.",
            "Concept": "Create a focused transformation story that contrasts the current category convention with a more distinctive outcome.",
            "Hook": "What if the familiar choice felt completely new?",
            "CTA": "Discover the difference.",
            "Why this concept": first_recommendation,
            "Format": "15–30 second vertical social video.",
            "Proof": "Use one visible product demonstration, credible claim, or testimonial.",
            "Testing plan": recommendations[:3] or [
                "Test two opening hooks.",
                "Test emotional versus functional messaging.",
                "Test early versus end-frame CTA placement.",
            ],
            "Ad concepts": [
                {
                    "name": "Pattern Interrupt",
                    "angle": "Break the dominant category convention.",
                    "best_for": platforms[:2],
                    "hook": "Everyone shows the product the same way. Here is what they miss.",
                    "execution": "Open on the category convention, interrupt it within two seconds, then show a clearer product outcome.",
                    "cta": "See what is different.",
                },
                {
                    "name": "Proof in Motion",
                    "angle": "Make the primary benefit immediately visible.",
                    "best_for": platforms[:2],
                    "hook": "Watch the difference happen.",
                    "execution": "Use a fast demonstration, one quantified proof point, and a clean benefit recap.",
                    "cta": "Try it for yourself.",
                },
                {
                    "name": "Human Moment",
                    "angle": "Use a relatable emotional situation.",
                    "best_for": platforms[:2],
                    "hook": "That moment when the simple choice changes everything.",
                    "execution": "Show a recognizable tension, introduce the product naturally, and end on an emotional payoff.",
                    "cta": "Make the moment yours.",
                },
            ],
            "Messaging tests": [
                {
                    "variable": "Hook",
                    "version_a": "Problem-led opening",
                    "version_b": "Outcome-led opening",
                    "success_metric": "Three-second hold rate",
                },
                {
                    "variable": "Proof",
                    "version_a": "Product demonstration",
                    "version_b": "Customer testimonial",
                    "success_metric": "Click-through rate",
                },
                {
                    "variable": "CTA timing",
                    "version_a": "CTA in the first five seconds",
                    "version_b": "CTA on the end card",
                    "success_metric": "Conversion rate",
                },
                {
                    "variable": "Message",
                    "version_a": "Functional benefit",
                    "version_b": "Emotional benefit",
                    "success_metric": "Engagement rate",
                },
            ],
            "Channel recommendations": [
                {
                    "platform": platform,
                    "recommendation": (
                        "Use a native vertical format, immediate first-frame clarity, "
                        "on-screen captions, and platform-specific pacing."
                    ),
                }
                for platform in platforms
            ],
            "Production checklist": [
                "Define one primary audience and one primary promise.",
                "Show the product or core tension in the first two seconds.",
                "Capture a clean product demonstration or proof moment.",
                "Create caption-safe vertical framing.",
                "Produce at least three hook variants.",
                "Deliver clean CTA and end-card variants.",
            ],
            "Optimization priorities": [
                "Improve the first three-second hold rate.",
                "Increase proof clarity before adding more claims.",
                "Test a stronger emotional payoff.",
                "Scale only after one hook and CTA combination wins.",
            ],
            "Experiment roadmap": [
                {
                    "phase": "Phase 1 · Hook validation",
                    "objective": "Identify the strongest first-frame message.",
                    "decision_rule": "Advance the variant with the highest three-second hold rate.",
                },
                {
                    "phase": "Phase 2 · Proof validation",
                    "objective": "Determine which proof mechanism improves intent.",
                    "decision_rule": "Advance the variant with the best click-through rate.",
                },
                {
                    "phase": "Phase 3 · Scale",
                    "objective": "Confirm the winning concept across platforms.",
                    "decision_rule": "Scale only when performance remains stable across two audiences.",
                },
            ],
        }

    @classmethod
    def _empty_ai_output(
        cls,
        query: MarketQuery,
        fallback: Dict[str, Any],
        status: str,
    ) -> Dict[str, Any]:
        return {
            "ai_available": False,
            "ai_status": status,
            "executive_summary": fallback["executive_summary"],
            "metric_insights": fallback["metric_insights"],
            "opportunity_gaps": fallback["opportunity_gaps"],
            "recommendations": fallback["recommendations"],
            "market_intelligence": {
                "winning_formats": [],
                "common_hooks": [],
                "product_positioning": [],
                "competitor_patterns": [],
                "creative_gaps": [],
                "strategic_takeaway": "",
                "audience_signals": [],
                "emotional_drivers": [],
                "response_patterns": [],
                "market_health": {
                    "signals": [],
                    "summary": "",
                },
                "proof_patterns": [],
                "priority_actions": [],
            },
            "creative_brief": cls._fallback_brief(query, fallback),
        }

    def generate(
        self,
        query: MarketQuery,
        features: List[CreativeFeatures],
        metrics: Dict[str, int],
        patterns: Dict[str, Any],
        fallback: Dict[str, Any],
    ) -> Dict[str, Any]:
        # Generate AI intelligence, with a complete deterministic fallback.
        if not settings.openrouter_api_key:
            return self._empty_ai_output(
                query,
                fallback,
                "OPENROUTER_API_KEY is not configured. Showing deterministic fallback strategy.",
            )

        if not features:
            return self._empty_ai_output(
                query,
                fallback,
                "No creative features were available. Showing deterministic fallback strategy.",
            )

        evidence = self._evidence_summary(features)

        required_schema = {
            "executive_summary": "Three concise evidence-grounded sentences.",
            "metric_insights": {
                "Collected": "One concise sentence.",
                "Unique": "One concise sentence.",
                "Duplicate rate": "One concise sentence.",
                "Video ads": "One concise sentence.",
                "Active ads": "One concise sentence.",
                "Total views": "One concise sentence.",
            },
            "market_intelligence": {
                "winning_formats": [
                    {
                        "label": "Format name",
                        "percentage": 0,
                        "why_it_matters": "Evidence-grounded interpretation",
                    }
                ],
                "common_hooks": [
                    {
                        "label": "Hook family or exact hook",
                        "percentage": 0,
                        "interpretation": "Evidence-grounded interpretation",
                    }
                ],
                "product_positioning": [
                    {
                        "label": "Positioning theme",
                        "percentage": 0,
                        "interpretation": "Evidence-grounded interpretation",
                    }
                ],
                "competitor_patterns": [
                    {
                        "pattern": "Observed convention",
                        "evidence": "Specific count or percentage",
                    }
                ],
                "creative_gaps": [
                    {
                        "gap": "Underused opportunity",
                        "evidence": "Specific count or percentage",
                        "recommended_test": "Concrete test",
                    }
                ],
                "strategic_takeaway": "Two concise next-step sentences.",
                "audience_signals": [
                    {
                        "label": "Audience segment or audience pattern",
                        "percentage": 0,
                        "interpretation": "Evidence-grounded audience interpretation"
                    }
                ],
                "emotional_drivers": [
                    {
                        "label": "Emotion or emotional pattern",
                        "percentage": 0,
                        "interpretation": "What this means for creative strategy"
                    }
                ],
                "response_patterns": [
                    {
                        "label": "CTA or response pattern",
                        "percentage": 0,
                        "interpretation": "What this means for conversion behavior"
                    }
                ],
                "market_health": {
                    "signals": [
                        {
                            "label": "Saturation, freshness, diversity, or activity",
                            "value": "Short value",
                            "interpretation": "Evidence-grounded explanation"
                        }
                    ],
                    "summary": "Two sentences on overall market health"
                },
                "proof_patterns": [
                    {
                        "pattern": "Observed proof or trust convention",
                        "evidence": "Specific count or percentage",
                        "recommendation": "How to improve proof"
                    }
                ],
                "priority_actions": [
                    {
                        "priority": "Short action title",
                        "confidence": "High, medium, or directional",
                        "why": "Evidence-grounded reason",
                        "action": "Specific action",
                        "success_metric": "Metric to monitor"
                    }
                ]
            },
            "opportunity_gaps": [
                "Three to five evidence-based opportunities."
            ],
            "recommendations": [
                "Three to five specific, testable actions."
            ],
            "creative_brief": {
                "Objective": "Measurable objective.",
                "Audience": "Audience supported by evidence.",
                "Insight": "Human tension supported by evidence.",
                "Concept": "Focused campaign platform.",
                "Hook": "Opening line.",
                "CTA": "Clear CTA.",
                "Why this concept": "Evidence-grounded rationale.",
                "Format": "Recommended format.",
                "Proof": "Proof mechanism.",
                "Testing plan": ["Three A/B tests."],
                "Ad concepts": [
                    {
                        "name": "Concept name",
                        "angle": "Distinct angle",
                        "best_for": ["Platform or funnel stage"],
                        "hook": "Opening line",
                        "execution": "Concrete execution",
                        "cta": "CTA",
                    }
                ],
                "Messaging tests": [
                    {
                        "variable": "Test variable",
                        "version_a": "A",
                        "version_b": "B",
                        "success_metric": "Metric",
                    }
                ],
                "Channel recommendations": [
                    {
                        "platform": "Selected platform",
                        "recommendation": "Native execution guidance",
                    }
                ],
                "Production checklist": [
                    "Concrete production requirement"
                ],
                "Optimization priorities": [
                    "Prioritized measurable optimization"
                ],
                "Experiment roadmap": [
                    {
                        "phase": "Phase name",
                        "objective": "What this phase validates",
                        "decision_rule": "Specific rule for advancing or stopping"
                    }
                ],
            },
        }

        prompt = {
            "task": (
                "Create market intelligence and an actionable creative strategy. "
                "Every claim must be traceable to supplied evidence."
            ),
            "market_query": query.model_dump(mode="json"),
            "metrics": metrics,
            "aggregated_evidence": evidence,
            "creative_records": self._feature_payload(features),
            "existing_pattern_evidence": {
                "winning_patterns": [
                    item.model_dump(mode="json")
                    for item in patterns["winning_patterns"]
                ],
                "top_hooks": [
                    item.model_dump(mode="json")
                    for item in patterns["top_hooks"]
                ],
                "messaging_breakdown": patterns["messaging_breakdown"],
                "creative_dna": patterns["creative_dna"],
            },
            "required_output_schema": required_schema,
            "rules": [
                "Return valid JSON only.",
                "Do not invent formats, audiences, claims, or percentages.",
                "Use supplied percentages whenever percentages are shown.",
                "Use dominant or common rather than winning unless performance evidence supports winning.",
                "Explicitly mark weak evidence as directional.",
                "Tie every recommendation to the selected brand and evidence.",
                "Generate exactly three distinct ad concepts.",
                "Generate at least four messaging tests.",
                "Generate one recommendation for each selected platform.",
                "Generate at least six production checklist items.",
                "Generate four optimization priorities ordered by impact.",
                "Generate a three-phase experiment roadmap with explicit decision rules.",
                "Generate audience signals, emotional drivers, and CTA/response patterns using only supplied percentages.",
                "Generate market health signals covering saturation, freshness, creative diversity, and activity when evidence supports them.",
                "Generate proof/trust patterns and exactly three priority market actions.",
                "Keep labels concise and user-friendly.",
            ],
        }

        try:
            response = self.client.complete(
                [
                    {
                        "role": "system",
                        "content": (
                            "You are a senior creative strategist and advertising analyst. "
                            "Return concise, defensible JSON only. Never fabricate evidence."
                        ),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(prompt, ensure_ascii=False),
                    },
                ]
            )
            parsed = parse_json_content(
                response["choices"][0]["message"]["content"]
            )
            if not isinstance(parsed, dict):
                raise ValueError("OpenRouter did not return a JSON object.")

            market_intelligence = parsed.get("market_intelligence", {})
            if not isinstance(market_intelligence, dict):
                market_intelligence = {}

            creative_brief = parsed.get("creative_brief", {})
            if not isinstance(creative_brief, dict) or not creative_brief:
                creative_brief = self._fallback_brief(query, fallback)

            return {
                "ai_available": True,
                "ai_status": "Generated by the configured OpenRouter model.",
                "executive_summary": str(
                    parsed.get("executive_summary")
                    or fallback["executive_summary"]
                ),
                "metric_insights": {
                    **fallback["metric_insights"],
                    **(
                        parsed.get("metric_insights")
                        if isinstance(parsed.get("metric_insights"), dict)
                        else {}
                    ),
                },
                "market_intelligence": market_intelligence,
                "opportunity_gaps": (
                    parsed.get("opportunity_gaps")
                    if isinstance(parsed.get("opportunity_gaps"), list)
                    else fallback["opportunity_gaps"]
                )[:5],
                "recommendations": (
                    parsed.get("recommendations")
                    if isinstance(parsed.get("recommendations"), list)
                    else fallback["recommendations"]
                )[:5],
                "creative_brief": creative_brief,
            }
        except Exception as exc:
            return self._empty_ai_output(
                query,
                fallback,
                (
                    "OpenRouter failed or returned invalid JSON. "
                    "Showing deterministic fallback strategy. "
                    f"Technical detail: {type(exc).__name__}."
                ),
            )
