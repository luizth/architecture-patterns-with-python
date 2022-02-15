from sqlalchemy import MetaData, Table, Column, Integer, String
from sqlalchemy.orm import mapper, registry, relationship

import model

mapper_registry = registry()
metadata = MetaData()

order_lines = Table(
    'order_lines',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('sku', String(255)),
    Column('qty', Integer, nullable=False),
    Column('orderid', String(255)),
)

mapper_registry.map_imperatively(model.OrderLine, order_lines)


def start_mappers():
    lines_mapper = mapper(model.OrderLine, order_lines)
