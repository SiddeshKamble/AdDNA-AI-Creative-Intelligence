from __future__ import annotations

from models.creative import CreativeFeatures

class RecommendationEngine:
    def generate(self, features: list[CreativeFeatures], pattern_presence: dict[str, int]) -> tuple[list[str], list[str]]:
        total = max(len(features), 1)
        opportunities: list[str] = []
        recommendations: list[str] = []

        checks = [
            ("Comparison hook", "Comparison-style ads are underused", "Test a clear side-by-side comparison against the category norm."),
            ("Humor", "Humor is rarely used", "Test one humor-led concept to create pattern interruption."),
            ("Founder-led voice", "Founder-led storytelling is limited", "Test a founder-led story that explains why the product was created."),
            ("Direct-response CTA", "CTA variation is weak", "Move a benefit-led CTA earlier and test at least three CTA variants."),
            ("Product-first opening", "Product visibility is not consistent", "Show the product within the first two seconds."),
            ("Fast-edit video", "Few short, fast-edit videos were detected", "Produce a 15–25 second fast-cut version for mobile feeds."),
        ]
        for key, gap, recommendation in checks:
            ratio = pattern_presence.get(key, 0) / total
            if ratio < 0.25:
                opportunities.append(gap)
                recommendations.append(recommendation)

        if not recommendations:
            recommendations = [
                "Create three hook variations around the dominant market pain point.",
                "Test a stronger proof point before the final CTA.",
                "Use a differentiated visual opening to avoid category sameness.",
            ]

        return opportunities[:5], recommendations[:5]
