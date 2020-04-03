import json
import time
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


def get_recomm_by_user(user_id, threshold=7.0):
    key_u = 'u' + str(user_id) + '_recomm'
    redis_conn = redis.Redis(connection_pool=redis_pool)
    try:
        redis_value = literal_eval(redis_conn.get(key_u).decode('utf-8'))
        redis_conn.close()
    except AttributeError:
        # log
        redis_conn.close()
        return []

    result = []
    for item in redis_value:
        if item[1] >= threshold:
            result.append(item[0])
    return result


class MessageQueue:
    def __init__(self, db_pool=None):
        if db_pool is None:
            self.redis_pool = redis_pool
        else:
            self.redis_pool = db_pool
        self._connection = redis.Redis(connection_pool=self.redis_pool)

    def __enter__(self):
        self._connection = redis.Redis(connection_pool=self.redis_pool)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._connection.close()

    def __del__(self):
        self._connection.close()

    def send(self, msg):
        return self._connection.lpush('MQ', msg)

    def get(self, timeout=None):
        if timeout is None:
            result = self._connection.rpop('MQ')
        elif isinstance(timeout, int):
            result = self._connection.brpop('MQ', timeout=timeout)
        else:
            result = ''
        return json.dumps(result.decode('utf-8'))

    def send_refresh_recomm_signal(self):
        return self._connection.lpush('MQ', 'refresh_recomm_signal')

    def wait_refresh_signal(self, timeout=0):
        while True:
            result = self._connection.brpop('MQ', timeout=timeout).decode('utf-8')
            if result is 'refresh_recomm_signal':
                return True
            else:
                self._connection.lpush('MQ', result)
                time.sleep(1)

