from recommender_system import task_manager
from web_app import create_app, db
from web_app.models.user_model import User, Role, Post
from web_app.models.movie_model import Movie, Genre, Company, Country, UserRatedMovie
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand, Migrate

app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Post=Post,
                Movie=Movie, Genre=Genre, Company=Company, Country=Country, UserRatedMovie=UserRatedMovie
                )


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    task_manager.run()
    manager.run()
