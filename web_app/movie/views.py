from flask import render_template, jsonify

from web_app.models.movie_model import Movie
from web_app.movie import movie


@movie.route('/')
def index():
    return render_template('movie/index.html')


@movie.route('api/pop_movie_list')
def pop_movie_list():
    q = Movie.query.order_by('vote_count')[:20]
    movieitems = []
    for movie in q:
        movieitems.append({'title': movie.title, 'tagline': movie.tagline,
                           'poster_link': movie.poster_link})
    return jsonify({'movieitems': movieitems,
                    'status': 'success'})
