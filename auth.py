from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from flask_login import login_user, login_required, logout_user, current_user
import json

auth = Blueprint('auth', __name__)

def load_allergies():
    with open('static/allergies.json') as f:
        return json.load(f)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('profile.view_profile'))
            else:
                flash('Invalid username or password', category='danger')
    except Exception as e:
        current_app.logger.error(f"Login failed: {e}")
        flash('An error occurred. Please try again.', category='danger')

    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    current_app.logger.info('Logout route accessed')
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    allergies_list = load_allergies()
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password1')
        diet_preferences = request.form.get('diet_preferences')
        allergies = request.form.getlist('allergies')

        user = User(email=email, username=username, password=password, diet_preferences=diet_preferences, allergies=allergies)

        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful!', category='success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            current_app.logger.error(f"Registration failed: {e}")
            flash('An error occurred. Please try again.', category='danger')

    return render_template('register.html', allergies_list=allergies_list)
