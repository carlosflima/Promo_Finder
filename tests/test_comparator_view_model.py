from app.comparator.view_model import build_columns


def test_columns_are_sorted_by_lowest_offer_and_limited_to_five():
    offers = [
        {"site": "B", "price": 20},
        {"site": "A", "price": 10},
        *({"site": "B", "price": n} for n in range(1, 7)),
    ]
    columns = build_columns(offers)
    assert [column.site for column in columns] == ["B", "A"]
    assert len(columns[0].offers) == 5
    assert columns[0].offers[0]["price"] == 1


def test_marketplace_sellers_are_separate_columns():
    columns = build_columns([
        {"site": "Marketplace", "seller": "Seller B", "price": 12},
        {"site": "Marketplace", "seller": "Seller A", "price": 10},
    ])
    assert [(c.site, c.seller) for c in columns] == [
        ("Marketplace", "Seller A"),
        ("Marketplace", "Seller B"),
    ]
