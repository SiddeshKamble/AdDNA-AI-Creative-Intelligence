from __future__ import annotations

from collections import Counter, defaultdict

from models.creative import CreativeFeatures
from models.report import EvidenceItem


class PatternEngine:
    def _evidence(self, label: str, ids: list[str], total: int) -> EvidenceItem:
        return EvidenceItem(
            label=label,
            count=len(ids),
            percentage=round((len(ids) / max(total, 1)) * 100),
            ad_ids=ids[:8],
        )

    def build(self, features: list[CreativeFeatures]) -> dict:
        total = len(features)
        pattern_ids: dict[str, list[str]] = defaultdict(list)
        for feature in features:
            mapping = {
                "Product-first opening": feature.product_first,
                "Founder-led voice": feature.founder_led,
                "Fast-edit video": feature.fast_edits,
                "Comparison hook": feature.comparison_hook,
                "Humor": feature.humor,
                "Problem-led opening": feature.opening_style == "Problem-led",
                "Direct-response CTA": bool(feature.cta),
                "UGC / lifestyle style": feature.visual_style == "UGC / Lifestyle",
            }
            for label, present in mapping.items():
                if present:
                    pattern_ids[label].append(feature.ad_id)

        winning = sorted(
            [self._evidence(label, ids, total) for label, ids in pattern_ids.items() if ids],
            key=lambda item: item.count,
            reverse=True,
        )[:6]

        hooks = [feature for feature in features if feature.hook]
        hook_counter = Counter(feature.hook for feature in hooks)
        hook_ids = defaultdict(list)
        for feature in hooks:
            hook_ids[feature.hook].append(feature.ad_id)
        top_hooks = [
            self._evidence(hook, hook_ids[hook], total)
            for hook, _ in hook_counter.most_common(5)
        ]

        positioning_counter = Counter(item for feature in features for item in feature.positioning)
        messaging = {
            label: round((count / max(sum(positioning_counter.values()), 1)) * 100)
            for label, count in positioning_counter.most_common(6)
        }

        def dominant(values: list[str], fallback: str = "Insufficient data") -> str:
            return Counter(values).most_common(1)[0][0] if values else fallback

        creative_dna = {
            "Primary emotion": dominant([x for f in features for x in f.emotions]),
            "Primary hook": dominant([f.opening_style for f in features]),
            "Primary format": dominant([f.creative_format for f in features]),
            "Visual style": dominant([f.visual_style for f in features]),
            "Dominant CTA": dominant([f.cta for f in features if f.cta]),
            "Tone": dominant([f.tone for f in features]),
        }

        return {
            "winning_patterns": winning,
            "top_hooks": top_hooks,
            "messaging_breakdown": messaging,
            "creative_dna": creative_dna,
            "pattern_presence": {key: len(value) for key, value in pattern_ids.items()},
        }
