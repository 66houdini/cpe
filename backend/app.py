from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_caching import Cache
from backend.config import config

db = SQLAlchemy()
migrate = Migrate()
cache = Cache()


def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    
    # Configure CORS with origins from config
    CORS(app, origins=app.config['CORS_ORIGINS'])

    # Register blueprints (routes)
    from backend.routes import scenario, models
    app.register_blueprint(scenario.bp)
    app.register_blueprint(models.bp)

    return app