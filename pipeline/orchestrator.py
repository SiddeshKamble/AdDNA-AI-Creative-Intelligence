from models.market import MarketQuery
from pipeline.collector import AdCollector
from pipeline.deduplicator import CreativeDeduplicator
from pipeline.feature_extractor import CreativeFeatureExtractor
from pipeline.language_filter import AdLanguageFilter
from pipeline.report_generator import ReportGenerator


class AdDNAPipeline:
    def __init__(self) -> None:
        self.collector = AdCollector()
        self.language_filter = AdLanguageFilter()
        self.deduplicator = CreativeDeduplicator()
        self.extractor = CreativeFeatureExtractor()
        self.report_generator = ReportGenerator()

    def run(self, query: MarketQuery) -> dict:
        collected_ads = self.collector.collect(query, deduplicate=False)

        language_result = self.language_filter.apply(
            collected_ads,
            english_only=query.english_only,
            minimum_confidence=query.language_confidence,
        )
        filtered_ads = language_result.kept_ads

        dedupe = self.deduplicator.deduplicate(filtered_ads)
        unique_ads = dedupe.unique_ads[: query.page_size]
        features = self.extractor.extract_all(unique_ads)

        report = self.report_generator.generate(
            query=query,
            collected_ads=collected_ads,
            unique_ads=unique_ads,
            duplicate_count=dedupe.duplicate_count,
            features=features,
        ).model_dump(mode="json")

        report["language_counts"] = language_result.language_counts
        report["language_removed_count"] = language_result.removed_count
        report["filtered_count"] = len(filtered_ads)
        return report
