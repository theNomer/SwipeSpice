from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from werkzeug.utils import secure_filename
from models import db, Recipe, Comment
import os

recipes = Blueprint('recipes', __name__)

@recipes.route('/recipes')
def view_recipes():
    all_recipes = Recipe.query.all()
    return render_template('recipes.html', recipes=all_recipes)

@recipes.route('/recipe/<int:recipe_id>')
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
def upload_recipe():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        allergies = request.form['allergies']
        diet_type = request.form['diet_type']
        prep_time = request.form['prep_time']
        image = request.files['image']

        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join('static/uploads', filename))
            image_url = url_for('static', filename='uploads/' + filename)
        else:
            image_url = None

        new_recipe = Recipe(
            title=title,
            description=description,
            ingredients=ingredients,
            instructions=instructions,
            allergies=allergies.split(',') if allergies else [],
            diet_type=diet_type,
            prep_time=prep_time,
            image_url=image_url,
            author_id=current_user.id  # Assuming you have a current_user object
        )

        db.session.add(new_recipe)
        db.session.commit()
        flash('Recipe uploaded successfully!', 'success')
        return redirect(url_for('recipes.view_recipes'))

    return render_template('upload_recipe.html')