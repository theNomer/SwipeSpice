import logging
from flask import Flask, redirect, url_for
from flask_login import LoginManager, login_required
from flask_migrate import Migrate
from config import Config
from models import db, User
from auth import auth as auth_blueprint
from profile import profile as profile_blueprint
from recipes import recipes as recipes_blueprint
from swipe import swipe as swipe_blueprint


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)


login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        app.logger.error(f"Error loading user: {e}")
        return None



app.register_blueprint(auth_blueprint, url_prefix='/')
app.register_blueprint(profile_blueprint)
app.register_blueprint(recipes_blueprint)
app.register_blueprint(swipe_blueprint)
@app.route('/')
def home():
    app.logger.info('Home route accessed')
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return 'Welcome to your dashboard!'




if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run()