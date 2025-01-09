from flask import Blueprint, render_template, jsonify, request
from models import db, Recipe, Favorite, SwipedRecipe
from flask_login import current_user, login_required

swipe = Blueprint('swipe', __name__)

@swipe.route('/swipe')
@login_required
def swipe_view():
    swiped_recipe_ids = [swiped.recipe_id for swiped in SwipedRecipe.query.filter_by(user_id=current_user.id).all()]
    recipes = Recipe.query.filter(~Recipe.id.in_(swiped_recipe_ids)).all()
    serialized_recipes = [{'id': recipe.id, 'title': recipe.title, 'image_url': recipe.image_url} for recipe in recipes]
    return render_template('swipe.html', recipes=serialized_recipes)

@swipe.route('/swipe/favorite', methods=['POST'])
@login_required
def add_to_favorites():
    recipe_id = request.json.get('recipe_id')
    if recipe_id:
        favorite = Favorite(user_id=current_user.id, recipe_id=recipe_id)
        swiped_recipe = SwipedRecipe(user_id=current_user.id, recipe_id=recipe_id)
        db.session.add(favorite)
        db.session.add(swiped_recipe)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 400

@swipe.route('/swipe/remove', methods=['POST'])
@login_required
def remove_from_swipe():
    recipe_id = request.json.get('recipe_id')
    if recipe_id:
        swiped_recipe = SwipedRecipe(user_id=current_user.id, recipe_id=recipe_id)
        db.session.add(swiped_recipe)
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 400