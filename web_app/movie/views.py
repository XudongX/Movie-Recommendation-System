import sqlalchemy
from flask import render_template, jsonify, request, redirect
from ast import literal_eval

from flask_login import current_user

from web_app import db
from web_app.models.movie_model import Movie, Genre, UserRatedMovie
from web_app.movie import movie
from web_app.util import db_model_serialize, api_error, api_success, get_recomm_by_movie_id


@movie.route('/', methods=['GET'])
def index():
    return render_template('movie/index.html')


@movie.route('api/movie_list', methods=['GET'])
def movie_list():
    page_num = request.args.get('page_num')
    genre_id = request.args.get('genre_id')
    # if page_num is None:
    #     return api_error('missing args: page_num')
    if genre_id is None or genre_id is '':
        q_movies = Movie.query.order_by(Movie.release_date.desc())[:30]
    else:
        q = Genre.query.filter_by(id=genre_id)
        if q.count() == 0:
            return api_error('genre_id error')
        q = q.first()
        q_movies = q.movies.order_by(Movie.release_date.desc())[:30]

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
                  'vote_average': round(q.vote_average, 1),
                  'vote_count': q.vote_count}
    return render_template('movie/detail.html', movie_info=movie_info)


@movie.route('api/genres', methods=['GET'])
def genres():
    q = Genre.query.all()
    genres_list = [{'id': i.id, 'name': i.name} for i in q]
    return api_success({'genres': genres_list})


@movie.route('api/get_user_rate', methods=['GET'])
def get_user_rate():
    if current_user.is_authenticated is False:
        return api_error('user not login!')
    movie_id = request.args.get('movie_id')
    if movie_id is None:
        return api_error('missing args: movie_id')
    movie_id = int(movie_id)
    rated = UserRatedMovie.query.filter_by(movie_id=movie_id, user_id=current_user.id).first()
    if rated is None:
        return api_error("user did not rate this movie")
    else:
        result = {'score': round(rated.score, 1), 'movie_id': rated.movie_id}
        return api_success(result)


@movie.route('api/rate', methods=['GET', 'POST'])
def rate_movie():
    if current_user.is_authenticated is False:
        return api_error('user not login!')
    movie_id = request.values.get('movie_id')
    score = request.values.get('score')
    if movie_id is None or score is None:
        return api_error('missing args: movie_id or score')
    movie_id = int(movie_id)
    score = float(score)
    rated = UserRatedMovie.query.filter_by(movie_id=movie_id, user_id=current_user.id).first()
    mov = Movie.query.filter_by(id=movie_id).first()
    if mov is None:
        return api_error("movie_id error, no such movie")
    if score > 10 or score < 0:
        return api_error("score out of range")
    if rated is None:
        # 如果评分不存在
        rated = UserRatedMovie(movie_id=movie_id, user_id=current_user.id, score=score)
        mov.vote_average = (mov.vote_average * mov.vote_count + score) / (mov.vote_count + 1)
        mov.vote_count += 1
    else:
        # 如果评分存在
        mov.vote_average = (mov.vote_average * mov.vote_count - rated.score + score) / mov.vote_count
        rated.score = score
    try:
        db.session.add(mov)
        db.session.add(rated)
        db.session.commit()
    except:
        db.session.rollback()
        return api_error("database reported a error, fail to commit")
    return api_success(None)


@movie.route('api/user_recommend')
def user_recommend():
    pass


@movie.route('api/related_recommend')
def related_recommend():
    movie_id = request.values.get("movie_id")
    if movie_id is None:
        return api_error('missing args: movie_id')

    recomm = get_recomm_by_movie_id(movie_id)
    q = Movie.query.filter(Movie.id.in_(recomm))

    movie_items = [{'movie_id': i.id, 'title': i.title,
                    'tagline': i.tagline, 'poster_link': i.poster_link}
                   for i in q]
    return api_success({'movieItems': movie_items})


@movie.route('api/general_recommend')
def general_recommend():
    pass
