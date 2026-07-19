from __future__ import annotations
import re
from dataclasses import dataclass
from models.advertisement import Advertisement

try:
    from langdetect import detect_langs
except ImportError:  # pragma: no cover
    detect_langs = None

@dataclass
class LanguageFilterResult:
    kept_ads: list[Advertisement]
    removed_count: int
    language_counts: dict[str, int]

class AdLanguageFilter:
    # Detect ad-copy language and optionally retain English ads only.

    ENGLISH_MARKERS = {
        "the", "and", "you", "your", "with", "for", "this", "that", "shop",
        "buy", "learn", "discover", "meet", "get", "new", "now", "more",
    }

    @staticmethod
    def _text(ad: Advertisement) -> str:
        return " ".join(
            part.strip()
            for part in [ad.title, ad.hook, ad.ad_copy, ad.transcript]
            if part and part.strip()
        )

    def detect(self, ad: Advertisement) -> tuple[str, float]:
        if ad.language:
            normalized = ad.language.lower().split("-")[0]
            if normalized:
                return normalized, 1.0

        text = self._text(ad)
        if not text:
            return "unknown", 0.0

        if detect_langs is not None and len(text) >= 20:
            try:
                result = detect_langs(text[:4000])
                if result:
                    return result[0].lang.lower(), float(result[0].prob)
            except Exception:
                pass

        words = re.findall(r"[a-zA-Z']+", text.lower())
        if not words:
            return "unknown", 0.0
        marker_hits = sum(word in self.ENGLISH_MARKERS for word in words)
        confidence = min(0.95, marker_hits / max(3, len(words) * 0.12))
        return ("en", confidence) if marker_hits >= 2 else ("unknown", confidence)

    def apply(
        self,
        ads: list[Advertisement],
        english_only: bool,
        minimum_confidence: float,
    ) -> LanguageFilterResult:
        kept: list[Advertisement] = []
        counts: dict[str, int] = {}
        removed = 0

        for ad in ads:
            language, confidence = self.detect(ad)
            ad.language = language
            counts[language] = counts.get(language, 0) + 1

            keep = not english_only or (
                language == "en" and confidence >= minimum_confidence
            )
            if keep:
                kept.append(ad)
            else:
                removed += 1

        return LanguageFilterResult(
            kept_ads=kept,
            removed_count=removed,
            language_counts=counts,
        )
