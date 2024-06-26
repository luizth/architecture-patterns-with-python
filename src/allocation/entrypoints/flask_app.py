from datetime import datetime

from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from allocation import config
from allocation.domain import model
from allocation.adapters import orm
from allocation.adapters import repository
from allocation.service_layer import services


orm.start_mappers()

get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))

app = Flask(__name__)


@app.route("/", methods=['GET'])
def hello_world():
    return jsonify({'hello': 'world'}), 201


@app.route("/add_batch", methods=["POST"])
def add_batch():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    services.add_batch(
        request.json["ref"],
        request.json["sku"],
        request.json["qty"],
        eta,
        repo,
        session,
    )
    return "OK", 201


@app.route("/allocate", methods=['POST'])
def allocate_endpoint():
    session = get_session()
    repo = repository.SqlAlchemyRepository(session)
    try:
        batchref = services.allocate(
            request.json['orderid'],
            request.json['sku'],
            request.json['qty'],
            repo,
            session,
        )
    except (model.OutOfStock, services.InvalidSku) as e:
        return jsonify({'message': str(e)}), 400
    return jsonify({'batchref': batchref}), 201
