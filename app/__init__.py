from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore
from config import Config
import os

db = SQLAlchemy()
migrate = Migrate()
security = Security()

def create_app(config_class=Config):
    """
    Fábrica de aplicaciones para crear instancias de la aplicación Flask.
    """
    app = Flask(__name__,
                instance_relative_config=True,
                template_folder='../templates',
                static_folder='static'
                )
    app.config.from_object(config_class)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db)

    from app.models.user import User, Role
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore)

    # Registrar Blueprints (módulos de la aplicación)
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.routes.recepcion import bp as recepcion_bp
    app.register_blueprint(recepcion_bp, url_prefix='/recepcion')

    from app.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp)
    
    from app.routes.desmotado import bp as desmotado_bp
    app.register_blueprint(desmotado_bp)

    from app.routes.calidad import bp as calidad_bp
    app.register_blueprint(calidad_bp)

    return app