from flask import Blueprint, render_template

swipe = Blueprint('swipe', __name__)

@swipe.route('/swipe')
def swipe_view():
    return render_template('swipe.html')