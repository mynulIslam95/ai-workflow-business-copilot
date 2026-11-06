import pytest
from app.core import classify, connect, create_request, review

@pytest.mark.parametrize("message,expected", [
    ("I need access to the dashboard", "access"),
    ("Please buy new equipment", "purchase"),
    ("I need vacation next month", "leave"),
    ("Can you help with a business process?", "general"),
])
def test_classification(message, expected):
    assert classify(message) == expected

def test_request_review_and_audit(tmp_path):
    with connect(str(tmp_path / "test.db")) as con:
        item = create_request(con, "Alex", "Please buy new equipment")
        assert item["status"] == "pending"
        assert item["category"] == "purchase"
        item = review(con, item["id"], "approved", "Manager", "Budget checked")
        assert item["status"] == "approved"
        actions = [r[0] for r in con.execute("SELECT action FROM audit ORDER BY id")]
        assert actions == ["created", "approved"]
        with pytest.raises(ValueError):
            review(con, item["id"], "rejected", "Manager", "Again")
