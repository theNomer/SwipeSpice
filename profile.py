from models import db, User, Recipe, Favorite
from flask_login import login_required, current_user
from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app, jsonify
import json

profile = Blueprint('profile', __name__)



def load_allergies():
    with open('static/allergies.json') as f:
        return json.load(f)

@profile.route('/profile', methods=['GET'])
@login_required
def view_profile():
    allergies_list = load_allergies()
    return render_template('profile.html', allergies_list=allergies_list)

@profile.route('/profile', methods=['POST'])
@login_required
def update_profile():
    email = request.form.get('email')
    username = request.form.get('username')
    diet_preferences = request.form.get('diet_preferences')
    allergies = request.form.getlist('allergies')
    new_password = request.form.get('new_password')

    try:
        current_user.email = email
        current_user.username = username
        current_user.diet_preferences = diet_preferences
        current_user.allergies = allergies
        if new_password:
            current_user.set_password(new_password)
        db.session.commit()
        flash('Profile updated successfully!', category='success')
    except Exception as e:
        current_app.logger.error(f"Profile update failed: {e}")
        flash('An error occurred. Please try again.', category='danger')

    return redirect(url_for('profile.view_profile'))

@profile.route('/favorite/<int:recipe_id>', methods=['POST'])
@login_required
def favorite_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    favorite = Favorite.query.filter_by(user_id=current_user.id, recipe_id=recipe_id).first()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'status': 'removed'})
    else:
        new_favorite = Favorite(user_id=current_user.id, recipe_id=recipe_id)
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify({'status': 'added'})