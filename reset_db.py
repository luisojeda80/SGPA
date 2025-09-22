from app import db
from flask_security import UserMixin, RoleMixin
import uuid

# Tabla de asociación para la relación muchos a muchos entre Usuarios y Roles
roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):
    """Modelo para los roles de usuario."""
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    @staticmethod
    def insert_roles():
        roles = {
            'Balancero': 'Nivel Básico.',
            'Administrativo': 'Nivel Intermedio.',
            'AdminPlanta': 'Nivel Completo de Planta.',
            'CasaCentral': 'Nivel Corporativo.'
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
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    planta_id = db.Column(db.Integer, db.ForeignKey('planta.id'), nullable=True)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

class Planta(db.Model):
    """Modelo para las plantas desmotadoras."""
    __tablename__ = 'planta'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    codigo = db.Column(db.String(10), unique=True, nullable=False)
    usuarios = db.relationship('User', backref='planta', lazy=True)

    @staticmethod
    def insert_plantas():
        plantas = [
            {'nombre': 'Planta Formosa', 'codigo': 'P01'},
            {'nombre': 'Planta General Belgrano', 'codigo': 'P02'}
        ]
        for p_data in plantas:
            planta = Planta.query.filter_by(codigo=p_data['codigo']).first()
            if planta is None:
                planta = Planta(**p_data)
                db.session.add(planta)
        db.session.commit()

