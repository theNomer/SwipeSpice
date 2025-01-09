from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    diet_preferences = db.Column(db.String(80), nullable=True)
    allergies = db.Column(db.ARRAY(db.String), nullable=True)

    favorite_recipes = db.relationship('Recipe', secondary='favorites', backref='users_who_favorited', overlaps="favorites")

    def __init__(self, email, username, password, diet_preferences=None, allergies=None):
        self.email = email
        self.username = username
        self.set_password(password)
        self.diet_preferences = diet_preferences
        self.allergies = allergies

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_favorite(self, recipe_id):
        return Favorite.query.filter_by(user_id=self.id, recipe_id=recipe_id).first() is not None

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.LargeBinary, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    allergies = db.Column(db.ARRAY(db.String), nullable=True)
    diet_type = db.Column(db.String(80), nullable=True)
    prep_time = db.Column(db.Integer, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('recipes', lazy=True))
    comments = db.relationship('Comment', backref='recipe', lazy=True)

    def __repr__(self):
        return f"<Recipe {self.title}>"


class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('favorites', lazy=True, overlaps="favorite_recipes,favorited_by"))
    recipe = db.relationship('Recipe', backref=db.backref('favorited_by', lazy=True, overlaps="favorites"))

    def __repr__(self):
        return f"<Favorite user_id={self.user_id} recipe_id={self.recipe_id}>"


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)  # The comment text
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Author of the comment
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)  # Associated recipe

    user = db.relationship('User', backref=db.backref('comments', lazy=True))  # Relationship to user

    def __repr__(self):
        return f"<Comment {self.id} by User {self.user_id} on Recipe {self.recipe_id}>"
