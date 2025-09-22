# C:/SGPA/app/models/user.py
from app import db
from flask_security import UserMixin, RoleMixin
from werkzeug.security import generate_password_hash
import uuid

# Tabla de asociación para la relación muchos a muchos entre Usuarios y Roles
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    """Modelo para los roles de usuario (Balancero, Administrativo, etc.)."""
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

    @staticmethod
    def insert_roles():
        """Crea o actualiza los roles básicos en la base de datos."""
        roles = {
            'Balancero': 'Nivel Básico: Solo registro y lectura de pesajes.',
            'Administrativo': 'Nivel Intermedio: Gestión de productores y autorización de pesajes.',
            'AdminPlanta': 'Nivel Completo: Control total de una planta.',
            'CasaCentral': 'Nivel Corporativo: Administración de todas las plantas.'
        }
        for r_name, r_desc in roles.items():
            role = Role.query.filter_by(name=r_name).first()
            if role is None:
                role = Role(name=r_name, description=r_desc)
                db.session.add(role)
        db.session.commit()

class User(db.Model, UserMixin):
    """Modelo para los usuarios del sistema."""
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    active = db.Column(db.Boolean(), default=True)
    
    # --- CAMPO AÑADIDO PARA LA SOLUCIÓN ---
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    # Relación con la planta a la que pertenece el usuario (puede ser null para Casa Central)
    planta_id = db.Column(db.Integer, db.ForeignKey('planta.id'), nullable=True)
    planta = db.relationship('Planta', backref='usuarios')

    # Relación muchos a muchos con los roles
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class Planta(db.Model):
    """Modelo para las plantas desmotadoras."""
    __tablename__ = 'planta'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    codigo = db.Column(db.String(3), unique=True, nullable=False) # ej: P01, P02
    ubicacion = db.Column(db.String(255))

    def __repr__(self):
        return f'<Planta {self.nombre}>'

    @staticmethod
    def insert_plantas():
        """Inserta las dos plantas iniciales si no existen."""
        plantas = [
            {'nombre': 'Planta Formosa', 'codigo': 'P01', 'ubicacion': 'Formosa, Argentina'},
            {'nombre': 'Planta Chaco', 'codigo': 'P02', 'ubicacion': 'Chaco, Argentina'}
        ]
        for p_data in plantas:
            planta = Planta.query.filter_by(codigo=p_data['codigo']).first()
            if planta is None:
                planta = Planta(**p_data)
                db.session.add(planta)
        db.session.commit()
