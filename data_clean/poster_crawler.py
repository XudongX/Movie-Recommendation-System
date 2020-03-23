import csv
import json

from MySQLdb import connect

import pymysql
import requests

movie_data = None
with pymysql.connect("localhost", "root", "", "graduation_project") as cursor:
    cursor.execute("SELECT id, title FROM movies WHERE imdb_id is null")
    movie_data = cursor.fetchall()

poster_data = []
counter = 0

db = pymysql.connect("localhost", "root", "", "graduation_project")
cursor = db.cursor()
sql = "UPDATE movies SET imdb_id=%s, poster_link=%s  WHERE id=%s"

for movie in movie_data:
    counter += 1
    id = movie[0]
    title = movie[1]
    response = requests.post('http://www.omdbapi.com/', params={'s': title, 'apikey': '29b9dbd7'})
    json_data = json.loads(response.text)
    if json_data['Response'] is 'False':
        print("counter: " + str(counter))
        print(movie)
        break
    try:
        json_data['Search']
    except KeyError:
        print(json_data)
        print("== KeyError ==")
        poster_data.append((id, 'no_result', ''))
    else:
        pd = json_data['Search'][0]
        poster_data.append((id, pd['imdbID'], pd['Poster']))
    row = poster_data[-1]
    print(row)
    try:
        cursor.execute(sql, (row[1], row[2], row[0]))
        db.commit()
    except:
        db.rollback()

db.close()
