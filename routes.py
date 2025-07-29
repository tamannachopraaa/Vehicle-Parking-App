from flask import Flask, render_template, redirect, url_for, session, flash, request
from models import AppUser, LotSlot, LotInfo, db, SlotReservation
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

def init_routes(app):

    @app.route('/', methods=['GET', 'POST'])
    def index():
        return redirect(url_for('login'))

    # Login
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
                    return redirect(url_for('admin_login'))  
                else:
                    return redirect(url_for('user_login'))
            else:
                flash('Invalid credentials')
        return render_template('login.html')

    # Register
    @app.route('/register')
    def register():
        return render_template('register.html')

    @app.route('/register', methods=['POST'])
    def register_post():
        uname = request.form.get('username')
        upass = request.form.get('password')
        confirm_pass = request.form.get('confirm_password')
        name = request.form.get('name')

        if not uname or not upass or not confirm_pass:
            flash('Please fill out all fields')
            return redirect(url_for('register'))

        if upass != confirm_pass:
            flash('Passwords do not match')
            return redirect(url_for('register'))

        user = AppUser.query.filter_by(uname=uname).first()
        if user:
            flash('Username already exists')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(upass)

        new_user = AppUser(uname=uname, upass=hashed_password, name=name)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    # Logout
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

    # Admin login
    @app.route('/admin_login')
    def admin_login():
        user = None
        if 'user_id' in session:
            user = AppUser.query.get(session['user_id'])
        
        lots = LotInfo.query.all()
        for lot in lots:
            available_count = LotSlot.query.filter_by(parent_id=lot.lot_id, slot_status='A').count()
            lot.available_count = available_count
        
        all_bookings = SlotReservation.query.order_by(SlotReservation.time_in.desc()).all()
        
        return render_template('admin_login.html', user=user, lots=lots, all_bookings=all_bookings)

    # User login
    @app.route('/user_login')
    def user_login():
        user = None
        available_slots = []
        
        if 'user_id' in session:
            user = AppUser.query.get(session['user_id'])
            
            lots = LotInfo.query.all()
            for lot in lots:
                
                available_count = LotSlot.query.filter_by(parent_id=lot.lot_id, slot_status='A').count()
                
                if available_count > 0:
                    lot.available_count = available_count
                    available_slots.append(lot)

        return render_template('user_login.html', user=user, available_slots=available_slots)

    
    # Slot add
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

        try:
            number_of_slots = int(number_of_slots)
            charges_per_hour = float(charges_per_hour)
        except ValueError:
            flash('Invalid number or charges.')
            return redirect(url_for('add_slot'))

        # Create new Lot Info
        new_lot = LotInfo(
            lot_title=lot_title,
            lot_location=location,
            lot_zip=pincode,
            total_slots=number_of_slots,
            rate_per_hr=charges_per_hour
        )
        db.session.add(new_lot)
        db.session.commit() 

        for _ in range(number_of_slots):
            new_slot = LotSlot(
                parent_id=new_lot.lot_id,
                slot_status='A' 
            )
            db.session.add(new_slot)

        db.session.commit() 

        flash('Parking lot and slots added successfully!')
        return redirect(url_for('admin_login'))
    
    # Slot view
    @app.route('/slot/<int:slot_id>/')
    def view_slot(slot_id):
        slot = LotInfo.query.get(slot_id) 
        if not slot:
            flash("Slot not found.")
            return redirect(url_for('admin_login'))
        return render_template('show_slot.html', slot=slot)

    # Slot delete
    @app.route('/slot/<int:slot_id>/delete')
    def delete_slot(slot_id):
        slot = LotInfo.query.get(slot_id)
        if not slot:
            flash("Slot not found.", 'danger')
            return redirect(url_for('admin_login'))
        
        active_bookings = db.session.query(SlotReservation).join(LotSlot).filter(
            LotSlot.parent_id == slot_id,
            SlotReservation.time_out.is_(None)
        ).count()
        
        return render_template('delete_slot.html', slot=slot, active_bookings=active_bookings)

    # Delete slot confirmation
    @app.route('/slot/<int:slot_id>/delete/confirmed', methods=['POST'])
    def delete_slot_confirmed(slot_id):
        """Deletes the slot after confirmation, only if no active bookings exist."""
        slot = LotInfo.query.get(slot_id)
        if not slot:
            flash("Slot not found.", 'danger')
            return redirect(url_for('admin_login'))
        
        active_bookings = db.session.query(SlotReservation).join(LotSlot).filter(
            LotSlot.parent_id == slot_id,
            SlotReservation.time_out.is_(None)
        ).count()
        
        if active_bookings > 0:
            flash(f"Cannot delete parking lot '{slot.lot_title}'. There are {active_bookings} active booking(s). Please wait for all bookings to be completed.", 'danger')
            return redirect(url_for('admin_login'))
        
        total_bookings = db.session.query(SlotReservation).join(LotSlot).filter(
            LotSlot.parent_id == slot_id
        ).count()
        
        if total_bookings > 0:
            flash(f"Warning: Deleting parking lot '{slot.lot_title}' will also delete {total_bookings} booking record(s). Are you sure?", 'danger')

        
        try:
            LotSlot.query.filter_by(parent_id=slot_id).delete()
            
            # Delete lot
            db.session.delete(slot)
            db.session.commit()
            
            flash(f"Parking lot '{slot.lot_title}' deleted successfully.", 'success')
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while deleting the parking lot. Please try again.", 'danger')
            print(f"Delete error: {e}")
        
        return redirect(url_for('admin_login'))

    # Slot edit
    @app.route('/slot/<int:slot_id>/edit')
    def edit_slot(slot_id):
        slot = LotInfo.query.get(slot_id)  
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

    # Slot booking
    @app.route('/slot/<int:lot_id>/book')
    def book_slot(lot_id):
        """Handles the booking of a parking slot."""
        user_id = session.get('user_id')
        if not user_id:
            flash("You must be logged in to book a slot.")
            return redirect(url_for('login'))

        lot = LotInfo.query.get(lot_id)
        if not lot:
            flash("Parking lot not found.")
            return redirect(url_for('user_login'))

        available_slot = LotSlot.query.filter_by(parent_id=lot_id, slot_status='A').first()
        if not available_slot:
            flash("All slots in this lot are currently booked.")
            return redirect(url_for('user_login'))

        try:
            # Book slot
            available_slot.slot_status = 'O'

            # booking record
            reservation = SlotReservation(
                booked_by=user_id,
                slot_taken=available_slot.slot_id,
                time_in=datetime.now()
            )
            
            db.session.add(reservation)
            db.session.commit() 
            
            flash("Slot booked successfully!")
            
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while booking the slot. Please try again.")
            print(f"Booking error: {e}")
    
        return redirect(url_for('user_login'))

    @app.route('/admin/booking/<int:booking_id>')
    def view_booking(booking_id):
        booking = SlotReservation.query.get_or_404(booking_id)
        return render_template('view_booking.html', booking=booking)

    @app.route('/slot/release/<int:booking_id>')
    def release_slot(booking_id):
        """Handles the release of a parking slot and calculates final cost."""
        user_id = session.get('user_id')
        if not user_id:
            flash("You must be logged in to release a slot.")
            return redirect(url_for('login'))

        booking = SlotReservation.query.get(booking_id)
        if not booking:
            flash("Booking not found.")
            return redirect(url_for('user_login'))

        if booking.booked_by != user_id:
            flash("You can only release your own bookings.")
            return redirect(url_for('user_login'))

        if booking.time_out:
            flash("This booking has already been completed.")
            return redirect(url_for('user_login'))

        try:
            # Set the checkout time
            booking.time_out = datetime.now()
            
            duration = booking.time_out - booking.time_in
            duration_hours = duration.total_seconds() / 3600
            
            import math
            duration_hours = max(1, math.ceil(duration_hours))
            
            lot = booking.reserved_slot.parent_lot
            hourly_rate = lot.rate_per_hr
            
            # Calculate charge
            booking.final_charge = duration_hours * hourly_rate
            
            # Release slot
            slot = booking.reserved_slot
            slot.slot_status = 'A'  
            
            
            db.session.commit()
            
            flash(f"Slot released successfully! Duration: {duration_hours} hours. Final charge: ₹{booking.final_charge:.2f}")
            
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while releasing the slot. Please try again.")
            print(f"Release error: {e}")  
        
        return redirect(url_for('user_login'))