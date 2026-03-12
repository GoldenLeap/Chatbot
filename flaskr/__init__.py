import os
from flask import Flask 
from flask import render_template

def create_app(test_conf=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
    )
    if test_conf is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_conf)
    os.makedirs(app.instance_path, exist_ok=True)
    
    @app.route("/")
    def home():
        return render_template('index.html')
    
    from . import db
    db.init_app(app)
    
    return app


