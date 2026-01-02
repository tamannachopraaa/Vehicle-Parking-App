from flask import Flask
from config import Config
from models import db, create_admin
from routes import init_routes

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    create_admin()   # ensures admin exists

init_routes(app)

if __name__ == "__main__":
    app.run()
