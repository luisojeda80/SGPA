from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore
from flask_bcrypt import Bcrypt
from config import Config
import os

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
security = Security()

def create_app(config_class=Config):
    """
    Fábrica de aplicaciones para crear instancias de la aplicación Flask.
    """
    app = Flask(__name__,
                instance_relative_config=True,
                # LÍNEA CORREGIDA: Apunta a la carpeta de plantillas principal
                template_folder='../templates',
                static_folder='static'
                )
    app.config.from_object(config_class)

    # Asegurarse de que la carpeta 'instance' exista
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    # Configuración de Flask-Security
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
    
    # --- NUEVO BLUEPRINT REGISTRADO ---
    from app.routes.desmotado import bp as desmotado_bp
    app.register_blueprint(desmotado_bp)


    return app
