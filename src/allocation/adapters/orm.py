from sqlalchemy import MetaData, Table, Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import registry, relationship

from allocation.domain import model


mapper_registry = registry()
metadata = MetaData()

batches = Table(
    'batches',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('reference', String(255)),
    Column('sku', String(255)),
    Column('_purchased_quantity', Integer, nullable=False),
    Column('eta', Date, nullable=True)
)

order_lines = Table(
    'order_lines',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('sku', String(255)),
    Column('qty', Integer, nullable=False),
    Column('orderid', String(255)),
)

allocations = Table(
    'allocations',
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id")),
)


def start_mappers():
    mapper_registry.map_imperatively(
        model.OrderLine,
        order_lines
    )

    mapper_registry.map_imperatively(
        model.Batch,
        batches,
        properties={
            '_allocations': relationship(model.OrderLine, secondary=allocations, collection_class=set)
        }
    )
