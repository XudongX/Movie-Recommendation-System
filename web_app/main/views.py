from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response
from flask_sqlalchemy import get_debug_queries
from . import main
from ..models.movie_model import Movie
from ..models.user_model import User


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


@main.route('/', methods=['GET', 'POST'])
def index():
    test = Movie.query
    test2 = User.query
    return render_template('index.html')
