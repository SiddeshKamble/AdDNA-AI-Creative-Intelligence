from models.market import MarketQuery
from providers.pipispy.adspy import PiPiSpyAdspy


def test_market_query_defaults():
    query = MarketQuery()
    assert query.current_page == 1
    assert query.page_size == 20
