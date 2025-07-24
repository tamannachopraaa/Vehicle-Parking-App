from flask import Flask
from config import Config
from models import db
from routes import init_routes

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
init_routes(app)  # Register routes

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
