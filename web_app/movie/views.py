from flask import render_template, jsonify, request
from ast import literal_eval

from web_app.models.movie_model import Movie, Genre
from web_app.movie import movie
from web_app.util import db_model_serialize, api_error, api_success


@movie.route('/', methods=['GET'])
def index():
    return render_template('movie/index.html')


@movie.route('api/movie_list', methods=['GET'])
def movie_list():
    page_num = request.args.get('page_num')
    genre_id = request.args.get('genre_id')
    # if page_num is None:
    #     return api_error('no page_num found')
    print(genre_id)
    if genre_id is None or genre_id is '':
        q_movies = Movie.query.order_by(Movie.vote_average.desc())[:30]
    else:
        q = Genre.query.filter_by(id=genre_id)
        if q.count() == 0:
            return api_error('genre_id error')
        q = q.first()
        q_movies = q.movies.order_by(Movie.vote_average.desc())[:30]

    movie_items = [{'movie_id': i.id, 'title': i.title,
                    'tagline': i.tagline, 'poster_link': i.poster_link}
                   for i in q_movies]
    return api_success({'movieItems': movie_items})


@movie.route('detail/<int:movie_id>', methods=['GET'])
def movie_detail(movie_id):
    q = Movie.query.filter_by(id=movie_id).first()
    movie_info = {'movie_id': q.id,
                  'poster_link': q.poster_link,
                  'title': q.title,
                  'tagline': q.tagline if q.tagline is not None else '',
                  'keywords': [i['name'] for i in literal_eval(q.keywords)],
                  'overview': q.overview,
                  'genres': [i.name for i in q.genres],
                  'release_date': q.release_date.date(),
                  'vote_average': q.vote_average,
                  'vote_count': q.vote_count}
    return render_template('movie/detail.html', movie_info=movie_info)


@movie.route('api/genres', methods=['GET'])
def genres():
    q = Genre.query.all()
    genres_list = [{'id': i.id, 'name': i.name} for i in q]
    return api_success({'genres': genres_list})


@movie.route('api/related_recommend')
def related_recommend():
    movie_id = request.values.get("movie_id")
    if movie_id is None:
        return api_error("no args found")

    q = Movie.query.order_by(Movie.vote_average.desc())[:5]
    movie_items = [{'movie_id': i.id, 'title': i.title,
                    'tagline': i.tagline, 'poster_link': i.poster_link}
                   for i in q]
    return api_success({'movieItems': movie_items})
