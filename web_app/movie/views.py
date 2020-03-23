from flask import render_template

from web_app.movie import movie


@movie.route('/')
def index():
    return render_template('movie/index.html')