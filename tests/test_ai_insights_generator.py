from pipeline.ai_insights import AIInsightGenerator


def test_ai_insight_generator_has_generate_method():
    generator = AIInsightGenerator()
    assert callable(generator.generate)


def test_ai_insight_generator_has_fallback_method():
    generator = AIInsightGenerator()
    assert callable(generator._empty_ai_output)
