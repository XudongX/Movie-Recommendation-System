from ast import literal_eval
from collections import defaultdict

import redis
from flask import jsonify
from sqlalchemy import inspect

from web_app import redis_pool


def db_model_serialize(model):
    return {c: getattr(model, c) for c in inspect(model).attrs.keys()}


def api_error(error_message):
    return jsonify({'message': error_message, 'status': 'error'})


def api_success(data, total_results=None, **kwargs):
    if total_results is None:
        return jsonify({'data': data, 'status': 'success'})
    else:
        return jsonify({'data': data, 'totalResults': total_results, 'status': 'success'})


def get_rank():
    redis_conn = redis.Redis(connection_pool=redis_pool)
    try:
        result = literal_eval(redis_conn.get('rank_a').decode('utf-8'))
        redis_conn.close()
    except AttributeError:
        # log
        redis_conn.close()
        return []
    return result


def get_recomm_by_movie_id(movie_id):
    key1 = 'm' + str(movie_id) + '_a'
    key2 = 'm' + str(movie_id) + '_b'
    redis_conn = redis.Redis(connection_pool=redis_pool)
    try:
        result1 = literal_eval(redis_conn.get(key1).decode('utf-8'))
        result2 = literal_eval(redis_conn.get(key2).decode('utf-8'))
        redis_conn.close()
    except AttributeError:
        # log
        redis_conn.close()
        return []

    # improved algorithm
    selection1 = list(set(result1[:20]).intersection(set(result2[:20])))
    selection2 = result1[:5] + result2[:8]
    final = set(selection2)
    final.update(set(selection1))
    return list(final)
