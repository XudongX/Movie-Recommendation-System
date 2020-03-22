import csv
from ast import literal_eval

genres_dict = {}
production_companies_dict = {}
production_countries_dict = {}

# output_movies = []

output_genres = []
output_movies_genres = []

output_companies = []
output_movies_companies = []

output_countries = []
output_movies_countries = []

with open("./tmdb_5000_movies.csv") as csv_file:
    reader = csv.reader(csv_file)
    next(reader)
    count = 0
    for row in reader:
        genre = row[1]
        movie_id = int(row[3])
        production_company = row[9]
        production_country = row[10]

        for item in literal_eval(genre):
            genres_dict[item['id']] = item['name']
            output_movies_genres.append([movie_id, item['id']])

        for item in literal_eval(production_company):
            production_companies_dict[item['id']] = item['name']
            output_movies_companies.append([movie_id, item['id']])

        for item in literal_eval(production_country):
            production_countries_dict[item['iso_3166_1']] = item['name']
            output_movies_countries.append([movie_id, item['iso_3166_1']])

        # print(i)
        # count += 1
        # if count > 5:
        #     break

for k, v in genres_dict.items():
    output_genres.append([k, v])

for k, v in production_companies_dict.items():
    output_companies.append([k, v])

for k, v in production_countries_dict.items():
    output_countries.append([k, v])

# print(output_genres)
# print(output_countries)
# print(output_companies)
# print(output_movies_genres)
# print(output_movies_countries)
# print(output_movies_companies)

with open('genres.csv', 'w') as csv_file:
    csv.writer(csv_file).writerows(output_genres)

with open('countries.csv', 'w') as csv_file:
    csv.writer(csv_file).writerows(output_countries)

with open('companies.csv', 'w') as csv_file:
    csv.writer(csv_file).writerows(output_companies)

with open('movies_genres.csv', 'w') as csv_file:
    csv.writer(csv_file).writerows(output_movies_genres)

with open('movies_countries.csv', 'w') as csv_file:
    csv.writer(csv_file).writerows(output_movies_countries)

with open('movies_companies.csv', 'w') as csv_file:
    csv.writer(csv_file).writerows(output_movies_companies)
