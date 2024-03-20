#!/usr/bin/python3
"""
Main app
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models import User, Base, Post
import hashlib
import secrets
import string

# Initialize Flask app
app = Flask(__name__)

# Generate a random string of ASCII letters, digits, and punctuation
secret_key = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(32))

# Set the Flask application's secret key
app.secret_key = secret_key

# Configure SQLAlchemy to connect to the database
engine = create_engine('mysql://root:root@localhost/platform_data')

# Create the tables in the database
Base.metadata.create_all(engine)

# Create a sessionmaker to handle database sessions
Session = sessionmaker(bind=engine)
dbsession = Session()


##############################################################################


@app.route('/', strict_slashes=False)
def index():
    """
    Home
    """
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login():
    """
    Login page
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Get the given information from database
        user = dbsession.query(User).filter_by(email=email).first()

        # Check if credentials are correct
        if user and user.password == hashlib.sha256(password.encode()).hexdigest():
            # Set up the session for the user
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            session['user_firstname'] = user.firstname
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    Log out. Adding a log out route is only for organization of code
    and more complex operations in future if possible. I preferred this
    method over just making the logout button act as a submit button (HTML)
    """
    session.clear()

    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'], strict_slashes=False)
def signup():
    """
    Signup page
    """
    if request.method == 'POST':
        firstname = request.form['fullname']
        lastname = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Hash the password using hashlib
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        new_user = User(
                firstname=firstname,
                lastname=lastname,
                email=email,
                password=hashed_password
                )
        # Adding new user to database
        dbsession.add(new_user)
        dbsession.commit()

        # Flash a success message
        flash('Account created successfully!', 'success')

        return redirect(url_for('login'))

    return render_template('signup.html')
    
@app.route('/addPost', methods=['GET', 'POST'], strict_slashes=False)
def add_post():
    
    if request.method == 'POST':
        curr_user = None
        if 'user_id' in session:
            curr_user = session['user_id']
        
        author = ""
        if curr_user:
            author = curr_user.firstname
        content = request.form['content']
        newPost = Post(
                author=author,
                content=content
                )
        print(newPost)
        # Adding new user to database
        dbsession.add(newPost)
        dbsession.commit()
        flash('Post created successfully!', 'success')
        print("starting")
        return redirect(url_for('index'))
    return render_template('post.html')

@app.route('/posts')
def show_posts():
    
    posts = dbsession.query(Post).all()
    return render_template('posts.html', posts=posts)

@app.route('/posts/<int:post_id>', strict_slashes=False)
def show_post_byId(post_id):
    
    post = dbsession.query(Post).get(post_id)
    if post:
        return render_template('profile.html', post=post)
    else:
        return "User not found", 404
    return render_template('posts.html', posts=[])

@app.route('/users')
def users():
    """
    All users page
    """
    users = dbsession.query(User).all()
    return render_template('users.html', users=users)

@app.route('/users/<int:user_id>')
def user_profile(user_id):
    """
    Show user profile
    """
    if 'user_id' in session:
        curr_user = session['user_id']

    user = dbsession.query(User).get(user_id)
    if user:
        if 'user_id' in session:
            curr_user = session['user_id']
            is_current_user = (user.id == curr_user)
        else:
            is_current_user = False
        return render_template('profile.html', user=user, is_current_user=is_current_user)
    else:
        return "User not found", 404

@app.route('/about', strict_slashes=False)
def about():
    """
    About page
    """
    return render_template('about.html')

@app.route('/navbar')
def navbar():
    """
    Navigation bar at top
    """
    return render_template('navbar.html')

# PLACEHOLDER FOR MORE ROUTES


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
