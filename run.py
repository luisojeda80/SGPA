# C:/SGPA/run.py
from app import create_app, db, security  # Importa 'security'
from app.models.user import User, Role, Planta

# Crear la aplicación Flask utilizando la fábrica de aplicaciones
app = create_app()

@app.shell_context_processor
def make_shell_context():
    """
    Proporciona un contexto al shell de Flask para facilitar las pruebas.
    Permite acceder a los modelos directamente en `flask shell`.
    """
    # Accede a user_datastore a través del objeto security
    return {'db': db, 'User': User, 'Role': Role, 'Planta': Planta, 'user_datastore': security.datastore}

if __name__ == '__main__':
    # Ejecutar la aplicación.
    # En un entorno de producción, se debe usar un servidor WSGI como Gunicorn.
    # El modo debug=True es solo para desarrollo.
    app.run(debug=True, port=5000)
    
# Function to create a Cloud Storage bucket