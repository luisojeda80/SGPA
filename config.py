# C:/SGPA/config.py
import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

# --- INICIO DE LA SOLUCIÓN ---
# Asegurarse de que la carpeta 'instance' exista antes de configurar la app.
# Esto es crucial para que los scripts como 'flask db' funcionen correctamente.
instance_path = os.path.join(basedir, 'instance')
os.makedirs(instance_path, exist_ok=True)
# --- FIN DE LA SOLUCIÓN ---

class Config:
    """Clase de configuración base para la aplicación Flask."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una-clave-secreta-muy-dificil-de-adivinar'
    
    # --- Configuración de la Base de Datos ---
    # Usar la ruta absoluta a la carpeta 'instance' que acabamos de verificar.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(instance_path, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Configuración de Flask-Security-Too ---
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT') or 'un-salt-muy-seguro-para-las-passwords'
    SECURITY_PASSWORD_HASH = 'bcrypt'
    
    # URLs de autenticación
    SECURITY_LOGIN_URL = '/login'
    SECURITY_LOGOUT_URL = '/logout'
    SECURITY_REGISTER_URL = '/register'
    
    # Vistas a las que redirigir después de las acciones
    SECURITY_POST_LOGIN_VIEW = '/'
    SECURITY_POST_LOGOUT_VIEW = '/login'
    SECURITY_POST_REGISTER_VIEW = '/'
    
    # Deshabilitar vistas no deseadas de Flask-Security
    SECURITY_CHANGEABLE = False
    SECURITY_RECOVERABLE = False
    SECURITY_REGISTERABLE = False
    
    # Habilitar protección CSRF
    WTF_CSRF_ENABLED = True
    
    # Contraseña para la base de datos (conceptual para SQLCipher)
    DB_PASSWORD = "Administrador/Formosa2025*"
