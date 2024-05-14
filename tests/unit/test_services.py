import pytest

from allocation.domain import model # Fully Decoupling the Service-Layer Tests from the Domain, keeping all in one place (Factory)
from allocation.adapters import repository
from allocation.service_layer import services


class FakeRepository(repository.AbstractRepository):

    # Mitigation: Keep All Domain Dependencies in Fixture Functions
    @staticmethod
    def for_batch(ref, sku, qty, eta=None):
        return FakeRepository([
            model.Batch(ref, sku, qty, eta),
        ])

    def __init__(self, batches):
        self._batches = set(batches)
    def add(self, batch):
        self._batches.add(batch)
    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)
    def list(self):
        return list(self._batches)


class FakeSession():
    committed = False

    def commit(self):
        self.committed = True


def test_add_batch():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, repo, session)
    assert repo.get("b1") is not None
    assert session.committed


def test_allocate_returns_allocation():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, repo, session)
    result = services.allocate("o1", "COMPLICATED-LAMP", 10, repo, session)
    assert result == "batch1"


def test_allocate_errors_for_invalid_sku():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "AREALSKU", 100, None, repo, session)
    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, repo, FakeSession())


def test_commits():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("batch1", "COMPLICATED-LAMP", 100, None, repo, session)
    services.allocate("o1", "COMPLICATED-LAMP", 10, repo, session)
    assert session.committed is True
