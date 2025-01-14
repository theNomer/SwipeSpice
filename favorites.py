from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from models import db, Recipe, Comment

favorites = Blueprint('favorites', __name__)

def format_comments(comments):
    return [
        {
            'author': comment.user.username,  # Assuming User model has a username field
            'content': comment.content
        }
        for comment in comments
    ]

@favorites.route('/favorites', methods=['GET'])
@login_required
def view_favorites():
    recipes = current_user.favorite_recipes
    return render_template('favorites.html', recipes=recipes)

@favorites.route('/recipe/<int:recipe_id>')
@login_required
def get_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    comments = format_comments(recipe.comments)
    return {
        'title': recipe.title,
        'description': recipe.description,
        'ingredients': recipe.ingredients,
        'instructions': recipe.instructions,
        'allergies': recipe.allergies,
        'diet_type': recipe.diet_type,
        'prep_time': recipe.prep_time,
        'image_url': recipe.image_url,
        'comments': comments
    }

@favorites.route('/recipe/<int:recipe_id>/comment', methods=['POST'])
@login_required
def add_comment(recipe_id):
    content = request.json.get('content')
    if not content:
        return {'success': False, 'message': 'Content is required'}, 400

    new_comment = Comment(
        content=content,
        user_id=current_user.id,
        recipe_id=recipe_id
    )
    db.session.add(new_comment)
    db.session.commit()

    return {
        'success': True,
        'comment': {
            'author': current_user.username,
            'content': new_comment.content
        }
    }