from flask import Blueprint, render_template, request, session
import boto3 

views = Blueprint('views', __name__)


@views.route('/')
def index():
    return render_template('index.html')

@views.route('/login')
def login():    
    return render_template('login.html')

@views.route('/home')
def home():
    return render_template('home.html')

@views.route('/music')
def music():
    return render_template('music.html')

