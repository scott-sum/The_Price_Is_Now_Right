from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_login import LoginManager

from .commands import create_tables
from .models import User
from .routes import main
from .extensions import db, login_manager

def create_app(config_file='settings.py'):
    # Instantiation
    app = Flask(__name__)
    app.config.from_pyfile('settings.py')
    bootstrap = Bootstrap(app) # allows use of flask-bootstrap
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # connects flask-login and database
    # provide user_loader callback
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    app.register_blueprint(main)

    app.cli.add_command(create_tables)

    return app

#if __name__ == '__main__':
 #   app.run(debug=True)
