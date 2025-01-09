from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from models import db, Recipe, Comment
import os
import json


recipes = Blueprint('recipes', __name__)

def load_allergies():
    with open('static/allergies.json') as f:
        return json.load(f)


@recipes.route('/recipes', methods=['GET'])
@login_required
def view_recipes():
    search = request.args.get('search', '')
    allergies = request.args.getlist('allergies')
    ingredients = request.args.get('ingredients', '')
    max_cook_time = request.args.get('max_cook_time', type=int)

    query = Recipe.query

    if search:
        query = query.filter((Recipe.title.ilike(f'%{search}%')) | (Recipe.description.ilike(f'%{search}%')))

    if allergies:
        for allergy in allergies:
            query = query.filter(Recipe.allergies.any(allergy))

    if ingredients:
        query = query.filter(Recipe.ingredients.ilike(f'%{ingredients}%'))

    if max_cook_time is not None:
        query = query.filter(Recipe.prep_time <= max_cook_time)

    recipes = query.all()

    with open('static/allergies.json') as f:
        allergies_list = json.load(f)

    return render_template('recipes.html', recipes=recipes, allergies=allergies_list)


@recipes.route('/recipe/<int:recipe_id>')
@login_required
def get_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    comments = [
        {
            'author': comment.user.username,  # Assuming User model has a username field
            'content': comment.content
        }
    for comment in recipe.comments]
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

@recipes.route('/recipe/<int:recipe_id>/comment', methods=['POST'])
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

@recipes.route('/upload_recipe', methods=['GET', 'POST'])
@login_required
def upload_recipe():
    allergies_list = load_allergies()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        allergies = request.form.getlist('allergies')
        diet_type = request.form['diet_type']
        prep_time = request.form['prep_time']
        image = request.files['image']

        if image:
            filename = secure_filename(image.filename)
            upload_path = os.path.join('static/uploads', filename)
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            image.save(upload_path)
            image_url = url_for('static', filename='uploads/' + filename)
        else:
            image_url = None

        new_recipe = Recipe(
            title=title,
            description=description,
            ingredients=ingredients,
            instructions=instructions,
            allergies=allergies,
            diet_type=diet_type,
            prep_time=prep_time,
            image_url=image_url,
            author_id=current_user.id
        )

        db.session.add(new_recipe)
        db.session.commit()
        flash('Recipe uploaded successfully!', 'success')
        return redirect(url_for('recipes.view_recipes'))

    return render_template('upload_recipe.html', allergies_list=allergies_list)