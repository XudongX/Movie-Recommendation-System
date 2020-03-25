from flask import render_template, jsonify

from web_app.models.movie_model import Movie, Genre
from web_app.movie import movie
from web_app.util import db_model_serialize, api_error, api_success


@movie.route('/', methods=['GET'])
def index():
    return render_template('movie/index.html')


@movie.route('api/movie_list', methods=['GET'])
def movie_list():
    q = Movie.query.order_by(Movie.vote_average.desc())[:30]
    movie_items = [{'movie_id': i.id, 'title': i.title,
                    'tagline': i.tagline, 'poster_link': i.poster_link}
                   for i in q]
    return api_success({'movieItems': movie_items})


@movie.route('api/movie_list/<int:genre_id>', methods=['GET'])
def movie_list_by_genre(genre_id):
    q = Genre.query.filter_by(id=genre_id)
    if q.count() == 0:
        return api_error('genre_id error')
    q = q.first()
    movie_by_genre = q.movies.order_by(Movie.vote_average.desc())[:30]
    movie_items = [{'movie_id': i.id, 'title': i.title,
                    'tagline': i.tagline, 'poster_link': i.poster_link}
                   for i in movie_by_genre]
    return api_success({'movieItems': movie_items})


@movie.route('detail/<int:movie_id>')
def movie_detail(movie_id):
    q = Movie.query.filter_by(id=movie_id).first()
    movie_info = {}
    # movie_info = db_model_serialize(q)
    return render_template('movie/detail.html', movie_info=q)


@movie.route('api/genres')
def genres():
    q = Genre.query.all()
    genres_list = [{'id': i.id, 'name': i.name} for i in q]
    return api_success({'genres': genres_list})
