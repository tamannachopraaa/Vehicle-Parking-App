from flask import redirect, render_template, request, flash, url_for
from models import AppUser, db
from werkzeug.security import generate_password_hash, check_password_hash

def init_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login')
    def login():
        return render_template('login.html')
    
    @app.route('/login', methods=['POST'])
    def login_post():
        uname = request.form.get('username')
        upass = request.form.get('password')

        user = AppUser.query.filter_by(uname=uname).first()
        if user and check_password_hash(user.upass, upass):
            flash('Login successful!')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))   

    @app.route('/register')
    def register():
        return render_template('register.html')

    @app.route('/register', methods=['POST'])
    def register_post():
        uname = request.form.get('username')
        upass = request.form.get('password')
        confirm_pass = request.form.get('confirm_password')
        name = request.form.get('name')

        # Step 1: Validate input
        if not uname or not upass or not confirm_pass:
            flash('Please fill out all fields')
            return redirect(url_for('register'))

        if upass != confirm_pass:
            flash('Passwords do not match')
            return redirect(url_for('register'))

        # Step 2: Check if user exists
        user = AppUser.query.filter_by(uname=uname).first()
        if user:
            flash('Username already exists')
            return redirect(url_for('register'))

        # Step 3: Hash password and save user
        hashed_password = generate_password_hash(upass)

        new_user = AppUser(uname=uname, upass=hashed_password, name=name)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
