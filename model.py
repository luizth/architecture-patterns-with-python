from datetime import date
from dataclasses import dataclass
from typing import NewType, Optional, List


Quantity = NewType("Quantity", int)
Sku = NewType("Sku", str)
Reference = NewType("Reference", str)

"""
class Batch:
    def __init__(self, ref: Reference, sku: Sku, qty: Quantity):
    self.sku = sku
    self.reference = ref
    self._purchased_quantity = qty
 """


class OutOfStock(Exception):
    pass


@dataclass(frozen=True)
class OrderLine:
    order_id: str
    sku: str
    qty: int


class Batch:

    def __init__(
            self, ref: str, sku: str, qty: int, eta: Optional[date]
    ):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations = set()  # type: Set[OrderLine]

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        return hash(self.reference)

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty


def allocate(line: OrderLine, batches: List[Batch]) -> str:
    try:
        batch: Batch = next(
            b for b in sorted(batches) if b.can_allocate(line)
        )
    except StopIteration:
        raise OutOfStock(f'Out of stock for sku {line.sku}')
    batch.allocate(line)
    return batch.reference
