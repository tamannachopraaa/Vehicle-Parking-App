#import datetime
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy()

# Registered User Table
class AppUser(db.Model):
    __tablename__ = 'app_users'
    uid = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(100), unique=True, nullable=False)
    upass = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    isAdmin = db.Column(db.Boolean, default=False, nullable=False)

    bookings = db.relationship('SlotReservation', backref='reserved_by', lazy=True)


# Parking Lot Table
class LotInfo(db.Model):
    __tablename__ = 'lots_info'
    lot_id = db.Column(db.Integer, primary_key=True)
    lot_title = db.Column(db.String(120), nullable=False)
    lot_location = db.Column(db.String(200))
    lot_zip = db.Column(db.String(10))
    rate_per_hr = db.Column(db.Float, nullable=False)
    total_slots = db.Column(db.Integer, nullable=False)
    
    slot_list = db.relationship('LotSlot', backref='parent_lot', cascade="all, delete", lazy=True)


# Individual Slot in a Lot
class LotSlot(db.Model):
    __tablename__ = 'lot_slots'
    slot_id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('lots_info.lot_id'), nullable=False)
    slot_status = db.Column(db.String(1), default='A')  # A=Available, O=Occupied

    current_reservation = db.relationship('SlotReservation', backref='reserved_slot', lazy=True, uselist=False)


# Reservation Data
class SlotReservation(db.Model):
    __tablename__ = 'slot_reservations'
    rid = db.Column(db.Integer, primary_key=True)
    booked_by = db.Column(db.Integer, db.ForeignKey('app_users.uid'), nullable=False)
    slot_taken = db.Column(db.Integer, db.ForeignKey('lot_slots.slot_id'), nullable=False)
    time_in = db.Column(db.DateTime, default=datetime.utcnow)
    time_out = db.Column(db.DateTime, nullable=True)
    final_charge = db.Column(db.Float, nullable=True)

def create_admin():
    from flask import current_app
    with current_app.app_context():
        admin = AppUser.query.filter_by(isAdmin=True).first()
        if not admin:
            admin_user = AppUser(
                uname='admin',
                upass=generate_password_hash('admin'),
                name='Admin User',
                isAdmin=True
            )
            db.session.add(admin_user)
            db.session.commit()



