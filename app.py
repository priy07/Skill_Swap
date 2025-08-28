from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import InputRequired, Length, Email, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from flask import send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
from dotenv import load_dotenv

import os
import mysql.connector

# Load environment variables
load_dotenv()

# App and Config Setup
app = Flask(__name__)
# Secret key from .env
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_secret')

# MySQL connection using SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Direct MySQL connection function
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASS'),
        database=os.getenv('DB_NAME')
    )

# Ensure upload directory exists
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200))
    location = db.Column(db.String(100))
    is_public = db.Column(db.Boolean, default=True)
    availability_mode = db.Column(db.String(255))
    availability_date = db.Column(db.Date)
    availability_remark = db.Column(db.Text)
    profile_photo = db.Column(db.String(255))
    skills_offered = db.Column(db.Text)  # Comma-separated skills
    skills_wanted = db.Column(db.Text)  # Comma-separated skills

class SwapRequest(db.Model):
    __tablename__ = 'swap_request'
    
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skill = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='Pending')
    feedback = db.Column(db.Text)

    # Relationships
    requester = db.relationship('User', foreign_keys=[requester_id], backref='requests_sent')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='requests_received')

# Forms
class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

class ProfileForm(FlaskForm):
    location = StringField('Location')
    skills_offered = TextAreaField('Skills Offered')
    skills_wanted = TextAreaField('Skills Wanted')
    availability = StringField('Availability')
    is_public = BooleanField('Make Profile Public')
    submit = SubmitField('Update Profile')

class SwapRequestForm(FlaskForm):
    skill = StringField('Skill to Request', validators=[InputRequired(), Length(min=1, max=100)])
    submit = SubmitField('Send Swap Request')

class FeedbackForm(FlaskForm):
    feedback = TextAreaField('Leave Feedback', validators=[InputRequired()])
    submit = SubmitField('Submit Feedback')

# User loader
@app.route('/src/<path:filename>')
def custom_static(filename):
    return send_from_directory(os.path.join(app.root_path, 'src'), filename)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    skill = request.args.get('skill')
    date = request.args.get('date')
    mode = request.args.get('mode')

    query = User.query.filter(User.id != current_user.id)  # Exclude current user
    if skill:
        query = query.filter(User.skills_offered.like(f"%{skill}%"))
    if mode:
        query = query.filter_by(availability_mode=mode)

    users = query.all()
    return render_template('dashboard.html', users=users)

# SINGLE PROFILE ROUTE - Combined and fixed
UPLOAD_FOLDER = os.path.join('static', 'profile_photos')

@app.route('/profile', methods=['GET', 'POST']) 
@login_required
def profile():
    form = ProfileForm()
    user = current_user

    if request.method == 'POST':
        # Update user info
        user.location = request.form.get('location')
        user.skills_offered = request.form.get('skills_offered_input')
        user.skills_wanted = request.form.get('skills_wanted_input')
        user.availability_mode = request.form.get('availability_mode')

        # Parse date
        date_str = request.form.get('availability_date')
        if date_str:
            try:
                user.availability_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format', 'error')

        user.availability_remark = request.form.get('availability_remark')
        user.is_public = bool(request.form.get('is_public'))

        # Handle profile photo upload
        profile_photo = request.files.get('profile_photo')
        if profile_photo and profile_photo.filename != '':
            filename = secure_filename(profile_photo.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
            filename = timestamp + filename

            # Full absolute path to save file
            upload_dir = os.path.join(current_app.root_path, UPLOAD_FOLDER)
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)  # Create folder if not exist

            filepath = os.path.join(upload_dir, filename)
            try:
                profile_photo.save(filepath)
                # Save relative path from 'static/', e.g. 'profile_photos/filename.jpg'
                user.profile_photo = f'profile_photos/{filename}'
            except Exception as e:
                flash(f'Error uploading file: {str(e)}', 'error')

        try:
            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'error')

    return render_template('profile.html', user=user, form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('register.html', form=form)
        
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(
            username=form.name.data,
            email=form.email.data,
            password=hashed_password
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            login_user(new_user)
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {str(e)}', 'error')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password', 'error')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/swap_request', methods=['GET', 'POST'])
@login_required
def swap_request():
    form = SwapRequestForm()
    receiver_id = request.args.get('receiver_id')

    if not receiver_id:
        flash("No user selected for swap request", "error")
        return redirect(url_for('dashboard'))

    receiver = User.query.get(receiver_id)
    if not receiver:
        flash("User not found", "error")
        return redirect(url_for('dashboard'))

    # Check if user is trying to send request to themselves
    if receiver.id == current_user.id:
        flash("You cannot send a swap request to yourself", "error")
        return redirect(url_for('dashboard'))

    # Check if request already exists
    existing_request = SwapRequest.query.filter_by(
        requester_id=current_user.id,
        receiver_id=receiver.id,
        status='Pending'
    ).first()
    
    if existing_request:
        flash("You already have a pending request with this user", "warning")
        return redirect(url_for('view_swaps'))

    if form.validate_on_submit():
        try:
            swap = SwapRequest(
                requester_id=current_user.id,
                receiver_id=receiver.id,
                skill=form.skill.data
            )
            db.session.add(swap)
            db.session.commit()
            flash(f'Swap request sent to {receiver.username} successfully!', 'success')
            return redirect(url_for('view_swaps'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error sending swap request: {str(e)}', 'error')

    return render_template('swap_request.html', form=form, receiver=receiver)

@app.route('/swap_requests')
@login_required
def view_swaps():
    # Get requests received by current user
    received = SwapRequest.query.filter_by(receiver_id=current_user.id).all()
    
    # Get requests sent by current user
    sent = SwapRequest.query.filter_by(requester_id=current_user.id).all()
    
    return render_template('swap_requests.html', received=received, sent=sent)

@app.route('/respond_swap/<int:swap_id>/<string:action>')
@login_required
def respond_swap(swap_id, action):
    swap = SwapRequest.query.get_or_404(swap_id)
    
    # Check if current user is the receiver of this request
    if swap.receiver_id != current_user.id:
        flash('You are not authorized to respond to this request', 'error')
        return redirect(url_for('view_swaps'))
    
    # Check if request is still pending
    if swap.status != 'Pending':
        flash('This request has already been responded to', 'warning')
        return redirect(url_for('view_swaps'))
    
    try:
        if action == 'accept':
            swap.status = 'Accepted'
            flash(f'Swap request from {swap.requester.username} accepted!', 'success')
        elif action == 'reject':
            swap.status = 'Rejected'
            flash(f'Swap request from {swap.requester.username} rejected.', 'info')
        else:
            flash('Invalid action', 'error')
            return redirect(url_for('view_swaps'))
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f'Error responding to request: {str(e)}', 'error')
    
    return redirect(url_for('view_swaps'))

@app.route('/feedback/<int:swap_id>', methods=['GET', 'POST'])
@login_required
def leave_feedback(swap_id):
    swap = SwapRequest.query.get_or_404(swap_id)
    
    # Check if current user is part of this swap
    if swap.requester_id != current_user.id and swap.receiver_id != current_user.id:
        flash('You are not authorized to leave feedback for this swap', 'error')
        return redirect(url_for('view_swaps'))
    
    # Check if swap is accepted
    if swap.status != 'Accepted':
        flash('You can only leave feedback for accepted swaps', 'error')
        return redirect(url_for('view_swaps'))
    
    # Check if feedback already exists
    if swap.feedback:
        flash('Feedback has already been submitted for this swap', 'warning')
        return redirect(url_for('view_swaps'))
    
    form = FeedbackForm()
    if form.validate_on_submit():
        try:
            swap.feedback = form.feedback.data
            db.session.commit()
            flash('Feedback submitted successfully!', 'success')
            return redirect(url_for('view_swaps'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting feedback: {str(e)}', 'error')
    
    return render_template('feedback.html', form=form, swap=swap)

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)