import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from ast import literal_eval
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class DemographicFiltering:
    def __init__(self, df, quantile_num=0.9):
        if not isinstance(df, pd.DataFrame):
            raise TypeError('DemographicFiltering need Pandas.DataFrame objects: df')
        self.df = df
        self.vote_average_mean = df['vote_average'].mean()  # vote_average的平均值
        self.vote_count_quantile = df['vote_count'].quantile(quantile_num)  # vote_count的分位数

    def _weighted_rating(self, elem):
        m = self.vote_count_quantile
        C = self.vote_average_mean
        v = elem['vote_count']
        R = elem['vote_average']
        # 基于IMDB的Weighted Rating计算公式
        return (v / (v + m) * R) + (m / (m + v) * C)

    def calculate(self):
        """
        :return: tuple(rank1: PandasArray, rank2: PandasArray)
        """
        q_movies = self.df[['id', 'title', 'vote_count', 'vote_average', 'popularity']].copy() \
            .loc[self.df['vote_count'] >= self.vote_count_quantile]
        q_movies.shape  # log
        # 定义一个新feature score，值为每行计算的weighted rating
        q_movies['score'] = q_movies.apply(self._weighted_rating, axis=1)
        # 对score列从大到小排序
        q_movies = q_movies.sort_values('score', ascending=False)
        pop_movies = self.df.sort_values('popularity', ascending=False)
        return q_movies['id'].array, pop_movies['id'].array


class ContentBasedFiltering:
    def __init__(self, df, results_num=100):
        if not isinstance(df, pd.DataFrame):
            raise TypeError('ContentBasedFiltering need Pandas.DataFrame objects: df')
        self.df = df
        self.indices = pd.Series(self.df.index, index=self.df['id'])  # 构造反向映射
        self.results_num = results_num

    def _get_recommendations(self, movie_id, cosine_sim):
        idx = self.indices[movie_id]  # 根据movie id获得矩阵中的行index

        # 从cosine_sim矩阵的idx行 构造一个pair:(index,sim_score), 放在list中。
        sim_scores = list(enumerate(cosine_sim[idx]))

        # 根据pair中的sim_score从大到小排序
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        if self.results_num is not None:
            sim_scores = sim_scores[1:self.results_num + 1]  # 第一个是自身，得到前results_num个similarity score最高的
        movie_indices = [i[0] for i in sim_scores]
        return self.df['id'].iloc[movie_indices].array  # 根据index返回id的PandasArray / 或者.values返回ndarray

    @classmethod
    def __get_director(cls, x):
        # 通过crew list得到导演的名字
        for i in x:
            if i['job'] == 'Director':
                return i['name']
        return np.nan

    @classmethod
    def __get_list(cls, x, max_names=5):
        # 将dict组成的list变为单纯的字符串list形式
        if isinstance(x, list):
            names = [i['name'] for i in x]
            # 限制返回的名字数量
            if len(names) > max_names:
                names = names[:max_names]
            return names
        # missing or malformed data
        return []

    @classmethod
    def _clean_data(cls, x):
        if isinstance(x, list):
            return [str.lower(i.replace(" ", "")) for i in x]  # lowercase、移除空格
        else:
            if isinstance(x, str):  # director列 lowercase、移除空格
                return str.lower(x.replace(" ", ""))
            else:
                return ''

    @classmethod
    def _create_soup(cls, x):
        # create "metadata soup"
        return ' '.join(x['keywords']) + ' ' + ' '.join(x['cast']) + ' ' + x['director'] + ' ' + ' '.join(x['genres'])

    def _calculate_b(self, movie_id):
        df2 = self.df.copy()
        features = ['cast', 'crew', 'keywords']
        for feature in features:  # 将str转换为list(dict())
            df2[feature] = df2[feature].apply(literal_eval)

        # 建立director feature
        df2['director'] = df2['crew'].apply(self.__get_director)

        features = ['cast', 'keywords']  # genres列在从db导入时已经格式化为list形式
        for feature in features:
            df2[feature] = df2[feature].apply(self.__get_list)

        # 对features应用clean_data().
        features = ['cast', 'keywords', 'director', 'genres']
        for feature in features:
            df2[feature] = df2[feature].apply(self._clean_data)

        df2['soup'] = df2.apply(self._create_soup, axis=1)

        count = CountVectorizer(stop_words='english')
        count_matrix = count.fit_transform(df2['soup'])

        cosine_sim2 = cosine_similarity(count_matrix, count_matrix)
        df2 = df2.reset_index()
        return self._get_recommendations(movie_id, cosine_sim2)

    def _calculate_a(self, movie_id):
        # 初始化TfidfVectorizer对象，stop_words会移除英文中冠词介词之类的词
        tfidf = TfidfVectorizer(stop_words='english')

        # 将NaN替换为空字符串
        self.df['overview'] = self.df['overview'].fillna('')

        # 构造TF-IDF矩阵
        tfidf_matrix = tfidf.fit_transform(self.df['overview'])
        tfidf_matrix.shape

        # 计算tfidf矩阵与自身的similarity矩阵
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        cosine_sim.shape

        return self._get_recommendations(movie_id, cosine_sim)

    def calculate(self, movie_id):
        """
        :param movie_id: int
        :return: tuple(recomm1: PandasArray, recomm2: PandasArray)
        """
        return self._calculate_a(movie_id), self._calculate_b(movie_id)


class CollaborativeFiltering:
    def __init__(self):
        pass
