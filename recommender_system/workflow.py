import redis
from sqlalchemy import create_engine
import pandas as pd
import numpy as np

from recommender_system.model import DemographicFiltering, ContentBasedFiltering, CollaborativeFiltering


def data_importing(db_str='mysql://localhost:3306/graduation_project?user=root&password=mysqlmysql'):
    engine = create_engine(db_str)
    df1 = pd.read_sql_query('SELECT * from credits',
                            engine.raw_connection())
    df2 = pd.read_sql_query(
        'SELECT id, keywords, overview, popularity, revenue, runtime, tagline, \
        title, vote_average, vote_count FROM movies',
        engine.raw_connection(),
        coerce_float=True  # 单精度会损失信息，但运算更快
    )
    df3 = pd.read_sql_query(
        'SELECT movies.id, genres.name FROM movies,genres,movies_genres \
        WHERE movies.id=movies_genres.movie_id AND genres.id=movies_genres.genre_id ORDER BY movies.id',
        engine.raw_connection()
    )
    df4 = pd.read_sql_query(
        'SELECT movies.id, companies.name FROM movies,companies,movies_companies \
        WHERE movies.id=movies_companies.movie_id AND companies.id=movies_companies.company_id \
        ORDER BY movies.id',
        engine.raw_connection()
    )
    rating_df = pd.read_sql_query('SELECT movie_id, user_id, score from user_rated_movies',
                                  engine.raw_connection(),
                                  coerce_float=True)
    user_df = pd.read_sql_query('SELECT id, email, username from users',
                                engine.raw_connection())
    df3 = df3.groupby('id')['name'].apply(list).reset_index()
    df3.columns = ['id', 'genres']
    df4 = df4.groupby('id')['name'].apply(list).reset_index()
    df4.columns = ['id', 'production_companies']
    df1.columns = ['id', 'tittle', 'cast', 'crew']
    df2 = df2.merge(df1, on='id', how='left')
    df2 = df2.merge(df3, on='id', how='left')
    df2 = df2.merge(df4, on='id', how='left')
    df2.reset_index()
    return df2, rating_df, user_df


def main():
    movie_df, rating_df, user_df = data_importing()

    pool = redis.ConnectionPool(host='0.0.0.0', port=6379)
    redis_conn = redis.Redis(connection_pool=pool)

    f1 = DemographicFiltering(movie_df, quantile_num=0.8)
    f1.calculate()
    f1_results = f1.get_results()
    redis_conn.set('rank_a', str(list(f1_results[0])))
    # rank_b 暂不需要
    # redis_conn.set('rank_b', str(list(f1_results[1])))

    f2 = ContentBasedFiltering(movie_df, results_num=60)
    f2.calculate()

    for movie_id in movie_df['id']:
        f2_results = f2.get_results(movie_id)
        key1 = 'm'+str(movie_id)+'_a'
        key2 = 'm' + str(movie_id) + '_b'
        redis_conn.set(key1, str(list(f2_results[0])))
        redis_conn.set(key2, str(list(f2_results[1])))

    redis_conn.close()


    # f3 = CollaborativeFiltering()
    # f3.calculate()
    # f3.get_results()


if __name__ == '__main__':
    main()
