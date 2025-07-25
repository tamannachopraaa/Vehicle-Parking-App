from flask import redirect, render_template, request, flash, url_for, session
from models import AppUser, db
from werkzeug.security import generate_password_hash, check_password_hash

def init_routes(app):
    @app.route('/')
    def index():
        return render_template('login.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            uname = request.form['uname']
            upass = request.form['upass']
            user = AppUser.query.filter_by(uname=uname).first()
            if user and check_password_hash(user.upass, upass):
                session['user_id'] = user.uid
                session['is_admin'] = user.isAdmin
                if user.isAdmin:
                    return redirect(url_for('admin_login'))  # Change to your admin route
                else:
                    return redirect(url_for('user_login'))   # Change to your user route
            else:
                flash('Invalid credentials')
        return render_template('login.html')

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

