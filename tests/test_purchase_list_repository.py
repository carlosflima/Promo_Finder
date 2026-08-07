from app.repository.purchase_list_repository import PurchaseListRepository
from app.api.purchase_lists import create_list


def test_purchase_list_round_trip(tmp_path):
    repo = PurchaseListRepository(tmp_path / "lists.db")
    created = create_list("Compras", repo)
    created["items"] = [{"title": "Produto", "quantity": 2, "total_price": 19.9}]
    repo.save(created)

    loaded = repo.get(created["id"])
    assert loaded is not None
    assert loaded["name"] == "Compras"
    assert loaded["items"][0]["quantity"] == 2


def test_delete_purchase_list(tmp_path):
    repo = PurchaseListRepository(tmp_path / "lists.db")
    created = create_list("Excluir", repo)
    assert repo.delete(created["id"]) is True
    assert repo.get(created["id"]) is None
