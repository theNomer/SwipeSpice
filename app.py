import logging
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from models import db, User
from auth import auth as auth_blueprint
from profile import profile as profile_blueprint
from recipes import recipes as recipes_blueprint
from swipe import swipe as swipe_blueprint
from favorites import favorites as favorites_blueprint

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_blueprint, url_prefix='/')
    app.register_blueprint(profile_blueprint)
    app.register_blueprint(recipes_blueprint)
    app.register_blueprint(swipe_blueprint)
    app.register_blueprint(favorites_blueprint)

    @app.route('/')
    def home():
        app.logger.info('Home route accessed')
        return redirect(url_for('auth.login'))

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception as e:
            app.logger.error(f"Error loading user: {e}")
            return None

    return app


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = create_app()
    app.run()
