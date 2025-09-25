from app import create_app
from app.models.user import db, User, Role, Planta
from app.models.operaciones import Productor
from werkzeug.security import generate_password_hash
import uuid

# Crear una instancia de la aplicación para tener el contexto correcto
app = create_app()

# Usar el contexto de la aplicación para interactuar con la base de datos
with app.app_context():
    print("--- INICIANDO REINICIO DE BASE DE DATOS ---")
    
    print("1. Borrando la base de datos anterior...")
    db.drop_all()
    
    print("2. Creando nuevas tablas...")
    db.create_all()

    print("3. Insertando datos iniciales (roles y plantas)...")
    Role.insert_roles()
    Planta.insert_plantas()

    # Obtener los roles y plantas para asignarlos a los usuarios
    casa_central_role = Role.query.filter_by(name='CasaCentral').first()
    admin_planta_role = Role.query.filter_by(name='AdminPlanta').first()
    administrativo_role = Role.query.filter_by(name='Administrativo').first()
    balancero_role = Role.query.filter_by(name='Balancero').first()
    planta1 = Planta.query.filter_by(codigo='P01').first()

    # --- Creación de Usuarios de Prueba ---
    print("4. Creando usuario Super Administrador (Casa Central)...")
    admin_user = User(
        email='admin@sgpa.com',
        password=generate_password_hash('Formosa2025*', method='pbkdf2:sha256'),
        first_name='Admin',
        last_name='Global',
        active=True,
        fs_uniquifier=str(uuid.uuid4()) # Campo requerido
    )
    admin_user.roles.append(casa_central_role)
    db.session.add(admin_user)

    print("5. Creando usuario Administrativo de Planta...")
    administrativo_user = User(
        email='admin.p01@sgpa.com',
        password=generate_password_hash('testing123', method='pbkdf2:sha256'),
        first_name='Ana',
        last_name='Gomez',
        active=True,
        fs_uniquifier=str(uuid.uuid4()),
        planta_id=planta1.id
    )
    administrativo_user.roles.append(administrativo_role)
    db.session.add(administrativo_user)

    print("6. Creando usuario Balancero...")
    balancero_user = User(
        email='balancero.p01@sgpa.com',
        password=generate_password_hash('testing123', method='pbkdf2:sha256'),
        first_name='Juan',
        last_name='Perez',
        active=True,
        fs_uniquifier=str(uuid.uuid4()),
        planta_id=planta1.id
    )
    balancero_user.roles.append(balancero_role)
    db.session.add(balancero_user)

    print("7. Creando productor de prueba...")
    p = Productor(nombre_completo='Productor de Prueba S.A.', cuit='30123456789', renpa='PR-123', activo=True)
    db.session.add(p)

    # Guardar todos los cambios en la base de datos
    db.session.commit()


    print("\n¡LISTO! La base de datos ha sido reiniciada exitosamente.")