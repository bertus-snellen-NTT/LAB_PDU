from flask import Blueprint, render_template
from app.services.example_service import get_welcome_message, get_about_info

main = Blueprint('main', __name__)


@main.route('/')
def index():
    message = get_welcome_message()
    return render_template('index.html', message=message)


@main.route('/about')
def about():
    info = get_about_info()
    return render_template('about.html', info=info)
