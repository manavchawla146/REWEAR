from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from google.oauth2 import id_token
from google.auth.transport import requests
import requests as http_requests
from . import db
from .models import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.verify_password(password):
        flash('Please check your login details and try again.')
        return redirect(url_for('main.signin'))
    
    login_user(user)
    
    if user.is_admin:
        return redirect(url_for('admin.index'))
    return redirect(url_for('main.home'))

@auth.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    
    email_exists = User.query.filter_by(email=email).first()
    username_exists = User.query.filter_by(username=name).first()
    
    if email_exists:
        flash('Email already exists.')
        return redirect(url_for('main.signin'))
    
    if username_exists:
        flash('Username already exists.')
        return redirect(url_for('main.signin'))
    
    new_user = User(
        username=name,
        email=email,
        password=password
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    login_user(new_user)
    return redirect(url_for('main.home'))

@auth.route('/google_login', methods=['POST'])
def google_login():
    try:
        data = request.get_json()
        if not data or 'credential' not in data:
            return jsonify({'success': False, 'error': 'No credential provided'}), 400

        token = data['credential']
        # Create a Request object for token verification
        req = requests.Request()
        # Verify the token with Google
        idinfo = id_token.verify_oauth2_token(
            token, 
            req, 
            current_app.config['GOOGLE_CLIENT_ID']
        )
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Invalid issuer')
        # Get user info from the token
        google_id = idinfo['sub']
        email = idinfo['email']
        name = idinfo.get('name', email.split('@')[0])
        picture = idinfo.get('picture')
        # Check if user exists
        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            # Check if email exists
            user = User.query.filter_by(email=email).first()
            if user:
                # Update existing user with Google ID
                user.google_id = google_id
                user.profile_picture = picture
            else:
                # Generate a unique username
                base_username = ''.join(e for e in name if e.isalnum()).lower()
                username = base_username
                counter = 1
                while User.query.filter_by(username=username).first():
                    username = f"{base_username}{counter}"
                    counter += 1
                user = User(
                    username=username,
                    email=email,
                    google_id=google_id,
                    profile_picture=picture
                )
                db.session.add(user)
                db.session.commit()
        # Log the user in
        login_user(user)
        return jsonify({
            'success': True,
            'redirect_url': url_for('main.home')
        })
    except ValueError as e:
        current_app.logger.error(f"Google login error: {str(e)}")
        return jsonify({'success': False, 'error': 'Invalid token'}), 400
    except Exception as e:
        current_app.logger.error(f"Google login error: {str(e)}")
        db.session.rollback()  # Roll back the session in case of error
        return jsonify({'success': False, 'error': str(e)}), 500

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@auth.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if not current_user.is_authenticated:
        flash('Please log in to add products to your cart.', 'info')
        return redirect(url_for('auth.login'))
    # ... existing code for adding to cart ...

@auth.route('/add_to_wishlist', methods=['POST'])
def add_to_wishlist():
    if not current_user.is_authenticated:
        flash('Please log in to add products to your wishlist.', 'info')
        return redirect(url_for('auth.login'))
    # ... existing code for adding to wishlist ...