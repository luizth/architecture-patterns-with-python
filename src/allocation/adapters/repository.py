import abc
from typing import List

from allocation.domain import model


class AbstractRepository(abc.ABC):

    @abc.abstractmethod  # Python will refuse to let you instantiate a class that does not implement all the abstractmethods defined in its parent class.
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session):
        self.session = session

    def add(self, batch: model.Batch):
        self.session.add(batch)

    def get(self, reference):
        return self.session.query(model.Batch).filter_by(reference=reference).one()

    def list(self):
        return self.session.query(model.Batch).all()


class FakeRepository(AbstractRepository):
    _batches: List[model.Batch]

    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch: model.Batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)


class TextualSqlAlchemyRepository(AbstractRepository):  # Implementation without ORM

    def __init__(self, session):
        self.session = session

    def add(self, batch: model.Batch):
        if batch.eta:
            insert_arg = 'INSERT INTO batches (reference, sku, _purchased_quantity, eta) ' \
                         f'VALUES ("{batch.reference}", "{batch.sku}", {batch._purchased_quantity}, {batch.eta})'
        else:
            insert_arg = 'INSERT INTO batches (reference, sku, _purchased_quantity) ' \
                         f'VALUES ("{batch.reference}", "{batch.sku}", {batch._purchased_quantity})'

        self.session.execute(insert_arg)
        [[batch_id]] = self.session.execute(
            'SELECT id FROM batches WHERE reference=:reference AND sku=:sku',
            dict(reference=batch.reference, sku=batch.sku)
        )
        return batch_id

    def get(self, reference):
        result = self.session.execute(
            'SELECT * FROM batches WHERE reference=:reference',
            dict(reference=reference)
        )
        raw_batch = result.fetchone()
        batch = model.Batch(
            ref=raw_batch['reference'],
            sku=raw_batch['sku'],
            qty=raw_batch['_purchased_quantity'],
            eta=raw_batch['eta'],
        )

        result = self.session.execute(
            'SELECT * FROM allocations WHERE batch_id=:batch_id',
            dict(batch_id=raw_batch['id'])
        )
        raw_allocations = result.fetchall()
        for item in raw_allocations:
            result = self.session.execute(
                'SELECT * FROM order_lines WHERE id=:orderline_id',
                dict(orderline_id=item['orderline_id'])
            )
            raw_orderline = result.fetchone()
            line = model.OrderLine(
                orderid=raw_orderline['orderid'],
                sku=raw_orderline['sku'],
                qty=raw_orderline['qty'],
            )
            model.allocate(line, [batch])

        return batch

    def list(self):
        batches = list()
        result = self.session.execute('SELECT * FROM batches')
        raw_batches = result.fetchall()
        for item in raw_batches:
            batch = model.Batch(
                ref=item['reference'],
                sku=item['sku'],
                qty=item['_purchased_quantity'],
                eta=item['eta'],
            )
            batches.append(batch)
        return batches
