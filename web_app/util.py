from flask import jsonify
from sqlalchemy import inspect


def db_model_serialize(model):
    return {c: getattr(model, c) for c in inspect(model).attrs.keys()}


def api_error(error_message):
    return jsonify({'message': error_message, 'status': 'error'})


def api_success(data):
    return jsonify({'data': data, 'status': 'success'})
