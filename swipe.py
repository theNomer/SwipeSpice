from flask import Blueprint, render_template
from flask_login import login_required

swipe = Blueprint('swipe', __name__)

@swipe.route('/swipe')
@login_required
def swipe_view():
    return render_template('swipe.html')