from flask import redirect, render_template, request, flash, url_for, session
from models import AppUser, LotSlot, LotInfo, db
from werkzeug.security import generate_password_hash, check_password_hash

def init_routes(app):
    @app.route('/', methods=['GET', 'POST'])
    def index():
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
    
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

    @app.route('/admin_login')
    def admin_login():
        user = None
        if 'user_id' in session:
            user = AppUser.query.get(session['user_id'])
        lots = LotInfo.query.all()
        return render_template('admin_login.html', user=user, lots=lots)

    @app.route('/user_login')
    def user_login():
        user = None
        if 'user_id' in session:
            user = AppUser.query.get(session['user_id'])
        return render_template('user_login.html', user=user)
    
    @app.route('/slot/add')
    def add_slot():
        return render_template('add_slot.html')

    @app.route('/slot/add', methods=['POST'])
    def add_slot_post():
        lot_title = request.form.get('lot_title')
        location = request.form.get('location')
        pincode = request.form.get('pincode')
        number_of_slots = request.form.get('number_of_slots')
        charges_per_hour = request.form.get('charges_per_hour')
        if not lot_title or not location or not pincode or not number_of_slots or not charges_per_hour:
            flash('Please fill out all fields')
            return redirect(url_for('add_slot'))

        new_lot = LotInfo(
            lot_title=lot_title,
            lot_location=location,
            lot_zip=pincode,
            total_slots=number_of_slots,
            rate_per_hr=charges_per_hour
        )
        db.session.add(new_lot)
        db.session.commit()
        flash('Parking lot added successfully!')
        return redirect(url_for('admin_login'))
    
    @app.route('/slot/<int:slot_id>/')
    def view_slot(slot_id):
        slot = LotInfo.query.get(slot_id)  # or LotSlot.query.get(slot_id) if you want individual slots
        if not slot:
            flash("Slot not found.")
            return redirect(url_for('admin_login'))
        return render_template('show_slot.html', slot=slot)

    @app.route('/slot/<int:slot_id>/delete')
    def delete_slot(slot_id):
        slot = LotInfo.query.get(slot_id)
        if not slot:
            flash("Slot not found.")
            return redirect(url_for('admin_login'))
        return render_template('delete_slot.html', slot=slot)


    @app.route('/slot/<int:slot_id>/delete/confirmed', methods=['POST'])
    def delete_slot_confirmed(slot_id):
        """Deletes the slot after confirmation."""
        slot = LotInfo.query.get(slot_id)
        if not slot:
            flash("Slot not found.")
            return redirect(url_for('admin_login'))
        db.session.delete(slot)
        db.session.commit()
        flash("Slot deleted successfully.")
        return redirect(url_for('admin_login'))

    @app.route('/slot/<int:slot_id>/edit')
    def edit_slot(slot_id):
        slot = LotInfo.query.get(slot_id)  # or LotSlot.query.get(slot_id) if you want individual slots
        if not slot:
            flash("Slot not found.")
            return redirect(url_for('admin_login'))
        return render_template('edit_slot.html', slot=slot)

    @app.route('/slot/<int:slot_id>/edit', methods=['POST'])
    def edit_slot_post(slot_id):
        slot = LotInfo.query.get(slot_id)
        if not slot:
            flash("Slot not found.")
            return redirect(url_for('admin_login'))
        name = request.form.get('lot_title')
        slot.lot_title = name
        slot.lot_location = request.form.get('location')
        slot.lot_zip = request.form.get('pincode')      
        slot.total_slots = request.form.get('number_of_slots')
        slot.rate_per_hr = request.form.get('charges_per_hour')     
        if not slot.lot_location or not slot.lot_zip or not slot.total_slots or not slot.rate_per_hr or not slot.lot_title:
            flash("All fields are required.")
            return redirect(url_for('edit_slot', slot_id=slot_id))
        
        db.session.commit()
        flash("Slot updated successfully.")
        return redirect(url_for('admin_login'))
