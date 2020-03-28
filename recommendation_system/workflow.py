from sqlalchemy import create_engine
import pandas as pd
import numpy as np

from recommendation_system.model import DemographicFiltering, ContentBasedFiltering


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


movie_df, rating_df, user_df = data_importing()
# f1 = DemographicFiltering(movie_df)
# print(type(f1.calculate()[0]))
#
f2 = ContentBasedFiltering(movie_df, results_num=200)
print(f2.calculate(49026))
