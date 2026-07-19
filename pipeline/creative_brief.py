from __future__ import annotations
from collections import Counter
from models.creative import CreativeFeatures

class CreativeBriefGenerator:
    @staticmethod
    def _dominant(values: list[str], fallback: str) -> str:
        return Counter(values).most_common(1)[0][0] if values else fallback

    def generate(self, features: list[CreativeFeatures], recommendations: list[str]) -> dict:
        audience = self._dominant(
            [item for feature in features for item in feature.audience],
            "Category buyers",
        )
        pain = self._dominant(
            [item for feature in features for item in feature.pain_points],
            "A recurring category frustration",
        )
        benefit = self._dominant(
            [item for feature in features for item in feature.benefits],
            "A simpler, better product experience",
        )
        emotion = self._dominant(
            [item for feature in features for item in feature.emotions],
            "Relief",
        )

        objective = "Increase click-through rate with a differentiated creative test."
        insight = (
            f"{audience} want {benefit.lower()} without the friction of {pain.lower()}."
        )
        concept = (
            f"Show a familiar moment of {pain.lower()} transforming into "
            f"{benefit.lower()}."
        )
        hook = f"What if {pain.lower()} finally felt easier?"
        cta = f"Try it today and get {benefit.lower()}."

        return {
            "Objective": objective,
            "Audience": audience,
            "Insight": insight,
            "Concept": concept,
            "Hook": hook,
            "CTA": cta,
            "Primary emotion": emotion,
            "Format": "20–30 second vertical UGC or product demonstration",
            "Proof": "Show one visible result, quantified claim, testimonial, or demonstration.",
            "Testing plan": recommendations[:3],
        }

    def script(self, brief: dict) -> list[dict[str, str]]:
        return [
            {
                "time": "0–3s",
                "scene": "Problem-led opening",
                "voiceover": brief.get("Hook", "What if this finally felt easier?"),
            },
            {
                "time": "3–8s",
                "scene": "Introduce the solution",
                "voiceover": brief.get("Concept", "Show the transformation."),
            },
            {
                "time": "8–16s",
                "scene": "Demonstrate the promise",
                "voiceover": brief.get("Insight", "Make the benefit immediately clear."),
            },
            {
                "time": "16–23s",
                "scene": "Add proof",
                "voiceover": brief.get("Proof", "Show one credible proof point."),
            },
            {
                "time": "23–30s",
                "scene": "CTA frame",
                "voiceover": brief.get("CTA", "Try it today."),
            },
        ]

    def shot_list(self, brief: dict) -> list[dict[str, str]]:
        return [
            {
                "shot": "1",
                "visual": "Show the audience experiencing the familiar problem.",
                "purpose": "Recognition",
            },
            {
                "shot": "2",
                "visual": "Reveal the product or solution within the first three seconds.",
                "purpose": "Clarity",
            },
            {
                "shot": "3",
                "visual": "Show the situation transforming into the desired outcome.",
                "purpose": "Concept",
            },
            {
                "shot": "4",
                "visual": brief.get("Proof", "Show one credible proof point."),
                "purpose": "Trust",
            },
            {
                "shot": "5",
                "visual": "Use a clean end card with the final CTA.",
                "purpose": "Conversion",
            },
        ]
