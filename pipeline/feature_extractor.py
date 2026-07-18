from __future__ import annotations

import re
from collections import OrderedDict

from models.advertisement import Advertisement
from models.creative import CreativeFeatures


class CreativeFeatureExtractor:
    PAIN_LEXICON = {
        "pain": "Pain",
        "hurt": "Pain",
        "strain": "Muscle strain",
        "injury": "Injury",
        "achilles": "Achilles discomfort",
        "knee": "Knee discomfort",
        "back": "Back discomfort",
        "slow": "Slow performance",
        "expensive": "High cost",
        "struggling": "Ongoing frustration",
        "tired": "Fatigue",
        "blister": "Blisters",
    }
    BENEFIT_LEXICON = {
        "faster": "Faster performance",
        "recover": "Faster recovery",
        "comfort": "Comfort",
        "pain-free": "Pain-free use",
        "pain free": "Pain-free use",
        "lightweight": "Lightweight feel",
        "durable": "Durability",
        "protect": "Protection",
        "support": "Support",
        "natural": "Natural movement",
        "sustainable": "Sustainability",
        "eco": "Sustainability",
        "convenient": "Convenience",
    }
    POSITIONING = {
        "premium": "Premium",
        "performance": "Performance",
        "speed": "Performance",
        "comfort": "Comfort",
        "eco": "Eco",
        "sustainable": "Eco",
        "easy": "Convenience",
        "convenient": "Convenience",
        "recovery": "Recovery",
        "recover": "Recovery",
        "durable": "Durability",
    }
    CTA_PATTERNS = [
        r"\bshop now\b",
        r"\bbuy now\b",
        r"\bget yours(?: here| today)?\b",
        r"\blearn more\b",
        r"\bstart (?:free|today)\b",
        r"\btry (?:it )?free\b",
        r"\bbook (?:a )?demo\b",
        r"\border now\b",
    ]

    @staticmethod
    def _unique(values: list[str]) -> list[str]:
        return list(OrderedDict.fromkeys(values))

    def _extract_hook(self, ad: Advertisement) -> str:
        if ad.hook:
            return ad.hook.strip()
        text = (ad.ad_copy or ad.transcript or ad.title or "").strip()
        if not text:
            return ""
        first_line = next((line.strip() for line in text.splitlines() if line.strip()), text)
        sentence = re.split(r"(?<=[.!?])\s+", first_line)[0]
        return sentence[:180]

    def _extract_cta(self, ad: Advertisement, text: str) -> str:
        if ad.cta_text:
            return ad.cta_text.strip()
        for pattern in self.CTA_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).title()
        return ""

    def extract(self, ad: Advertisement) -> CreativeFeatures:
        text = ad.creative_text
        lower = text.lower()
        hook = self._extract_hook(ad)
        cta = self._extract_cta(ad, text)
        pains = self._unique([label for token, label in self.PAIN_LEXICON.items() if token in lower])
        benefits = self._unique([label for token, label in self.BENEFIT_LEXICON.items() if token in lower])
        positioning = self._unique([label for token, label in self.POSITIONING.items() if token in lower])

        proof_points = []
        for line in text.splitlines():
            cleaned = line.strip(" •✅-\t")
            if cleaned and (re.search(r"\b\d+(?:%|x|\+)?\b", cleaned) or "reported" in cleaned.lower() or "approved" in cleaned.lower()):
                proof_points.append(cleaned[:180])

        audience = []
        audience_terms = {
            "runner": "Runners",
            "running": "Runners",
            "pickleball": "Pickleball players",
            "athlete": "Athletes",
            "women": "Women",
            "men": "Men",
            "mom": "Parents",
            "founder": "Entrepreneurs",
            "designer": "Designers",
        }
        audience.extend(label for token, label in audience_terms.items() if token in lower)

        emotions = []
        emotion_terms = {
            "fear": "Fear",
            "pain": "Relief",
            "finally": "Hope",
            "confident": "Confidence",
            "love": "Desire",
            "frustrat": "Frustration",
        }
        emotions.extend(label for token, label in emotion_terms.items() if token in lower)

        comparison = any(term in lower for term in [" vs ", "versus", "compared", "instead of", "unlike", "nike", "adidas"])
        humor = any(term in lower for term in ["lol", "funny", "hilarious", "😂", "joke"])
        founder_led = "founder" in lower or "i built" in lower or "our story" in lower
        product_first = bool(ad.title or ad.image_url or ad.video_url) and not hook.lower().startswith(("if ", "still ", "what if", "why "))

        if re.search(r"\bstill\b|\bstruggling\b|\btired of\b|\bproblem\b", hook.lower()):
            opening_style = "Problem-led"
        elif re.search(r"\bmeet\b|\bintroducing\b|\bnew\b", hook.lower()):
            opening_style = "Product introduction"
        elif "?" in hook:
            opening_style = "Question-led"
        elif comparison:
            opening_style = "Comparison"
        else:
            opening_style = "Benefit-led"

        creative_format = "Video" if ad.video_url else "Image" if ad.image_url or ad.thumbnail_url else "Copy-led"
        visual_style = "UGC / Lifestyle" if any(term in lower for term in ["i ", "my ", "routine", "day", "story"]) else "Product-led"
        tone = "Urgent" if any(term in lower for term in ["now", "today", "limited", "don't wait"]) else "Educational" if proof_points else "Direct response"

        confidence = 0.45
        confidence += 0.1 if hook else 0
        confidence += 0.1 if cta else 0
        confidence += 0.1 if pains or benefits else 0
        confidence += 0.1 if ad.video_url or ad.image_url else 0
        confidence += 0.1 if proof_points else 0

        return CreativeFeatures(
            ad_id=ad.source_id,
            provider=ad.provider,
            detected_brand=ad.brand,
            platforms=ad.platforms,
            hook=hook,
            cta=cta,
            pain_points=pains,
            benefits=benefits,
            proof_points=self._unique(proof_points)[:5],
            audience=self._unique(audience),
            positioning=positioning or ["General"],
            emotions=self._unique(emotions) or ["Neutral"],
            creative_format=creative_format,
            opening_style=opening_style,
            visual_style=visual_style,
            tone=tone,
            product_first=product_first,
            founder_led=founder_led,
            comparison_hook=comparison,
            humor=humor,
            fast_edits=bool(ad.video_url and ad.duration_seconds and ad.duration_seconds <= 25),
            confidence=min(confidence, 0.95),
        )

    def extract_all(self, ads: list[Advertisement]) -> list[CreativeFeatures]:
        return [self.extract(ad) for ad in ads]
