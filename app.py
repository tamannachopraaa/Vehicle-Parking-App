from flask import Flask, session
from config import Config
from models import db, create_admin, AppUser
from routes import init_routes

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()     #  THIS LINE FIXES REGISTER ERROR
    create_admin()

init_routes(app)


@app.context_processor
def inject_nav_context():
    user_id = session.get('user_id')
    user = AppUser.query.get(user_id) if user_id else None
    return {
        'nav_user': user,
        'nav_is_admin': bool(session.get('is_admin'))
    }

if __name__ == "__main__":
    app.run()
