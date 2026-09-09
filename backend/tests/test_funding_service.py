from ml_engine.funding_service import FundingService


def test_amount_parser():
    assert FundingService._parse_amount("I need ₹5 lakh for dairy") == 500000
    assert FundingService._parse_amount("2.5 crore project") == 25000000
    assert FundingService._parse_amount("no amount here") is None


def test_category_detection():
    assert FundingService.detect_category("I want to start a dairy business") == "dairy"
    assert FundingService.detect_category("need a kirana shop") == "retail"
    assert FundingService.detect_category("I want a tailoring unit") == "textiles"
    assert FundingService.is_funding_query("what loan can I get?") is True
    assert FundingService.is_funding_query("how should I price my product?") is False


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, *args):
        pass

    def fetchall(self):
        return self.rows


class FakeConn:
    def __init__(self, rows):
        self.rows = rows

    def cursor(self):
        return FakeCursor(self.rows)

    def close(self):
        pass


def test_scheme_ranking_uses_stored_project_range(monkeypatch):
    rows = [
        (1, "Scheme A", "A", "Dairy support", 100000, 1000000, .1, .9, 900000, 7.0, 60, 6, None, "v1", None, None, True),
        (2, "Scheme B", "B", "General", 2000000, 5000000, .2, .8, 4000000, 8.0, 60, 6, None, "v1", None, None, True),
    ]
    service = FundingService("fake")
    monkeypatch.setattr(service, "_connect", lambda: FakeConn(rows))
    result = service.list_schemes(project_cost=500000, category="dairy", limit=2)
    assert result[0]["scheme_code"] == "A"
    assert result[0]["match_score"] > result[1]["match_score"]


def test_loan_amount_outside_range_is_not_eligible(monkeypatch):
    rows = [
        (1, "LP1", "Bank", "Term Loan", "Bank", "India", "National", {"dairy": True}, 100000, 500000, 8.0, 10.0, "fixed", 12, 60, 3, 1.0, 10.0, False, None, 18, 65, 650, 12, {}, "https://example.com", {}, True),
    ]
    service = FundingService("fake")
    monkeypatch.setattr(service, "_connect", lambda: FakeConn(rows))
    result = service.list_loans(loan_amount=750000, category="dairy", limit=1)
    assert result[0]["eligible_on_supplied_data"] is False


def test_chat_context_contains_structured_funding(monkeypatch):
    rows_scheme = [
        (1, "Dairy Scheme", "DS1", "Dairy funding", 100000, 1000000, .1, .9, 900000, 7.0, 60, 6, None, "v1", None, None, True),
    ]
    rows_loan = [
        (1, "LP1", "Bank", "Dairy Loan", "Bank", "India", "National", {"dairy": True}, 100000, 500000, 8.0, 10.0, "fixed", 12, 60, 3, 1.0, 10.0, False, None, 18, 65, 650, 12, {}, "https://example.com", {}, True),
    ]
    class Service(FundingService):
        def __init__(self): pass
        def list_schemes(self, **kwargs):
            return FundingService.list_schemes(self, **kwargs)
    service = FundingService("fake")
    calls = iter([FakeConn(rows_scheme), FakeConn(rows_loan)])
    monkeypatch.setattr(service, "_connect", lambda: next(calls))
    context = service.chat_context("I need a dairy loan of 5 lakh")
    assert "SCHEME OPTIONS:" in context
    assert "LOAN OPTIONS:" in context
    assert "Dairy Loan" in context
