from flask import Flask
from config import Config
from models import db, create_admin,reset_all
from routes import init_routes

app = Flask(__name__)  # This is where app is defined
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    #reset_all()    
    create_admin()


init_routes(app)  # Pass the app instance to init_routes

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
