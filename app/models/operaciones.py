from app import db
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property

# Importamos los modelos de usuario necesarios para las relaciones
from .user import User

class Productor(db.Model):
    """Modelo para los productores de algodón."""
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(200), nullable=False)
    cuit = db.Column(db.String(13), unique=True, nullable=False)
    renpa = db.Column(db.String(20))
    telefono = db.Column(db.String(50))
    email = db.Column(db.String(120))
    activo = db.Column(db.Boolean, default=True)

class Chofer(db.Model):
    """Modelo para los choferes."""
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(150), nullable=False)
    dni = db.Column(db.String(10), unique=True, nullable=False)

class Vehiculo(db.Model):
    """Modelo para los vehículos."""
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10), unique=True, nullable=False)

class Carga(db.Model):
    """Modelo principal para registrar las cargas de algodón."""
    id = db.Column(db.Integer, primary_key=True)
    lote_id = db.Column(db.String(20), unique=True, nullable=False)
    fecha_entrada = db.Column(db.DateTime, default=datetime.utcnow)
    peso_bruto = db.Column(db.Float, nullable=False)
    peso_tara = db.Column(db.Float)
    fecha_salida = db.Column(db.DateTime)
    estado = db.Column(db.String(50), default='Pendiente Salida')
    numero_bascula = db.Column(db.Integer)
    placa_acoplado = db.Column(db.String(10))
    
    # --- CAMPOS NUEVOS AÑADIDOS ---
    dtv = db.Column(db.String(50))
    humedad = db.Column(db.Float)
    observaciones_romaneo = db.Column(db.Text)

    planta_id = db.Column(db.Integer, db.ForeignKey('planta.id'), nullable=False)
    productor_id = db.Column(db.Integer, db.ForeignKey('productor.id'), nullable=False)
    chofer_id = db.Column(db.Integer, db.ForeignKey('chofer.id'), nullable=False)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculo.id'), nullable=False)
    usuario_balancero_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    usuario_salida_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    productor = db.relationship('Productor')
    chofer = db.relationship('Chofer')
    vehiculo = db.relationship('Vehiculo')
    usuario_balancero = db.relationship('User', foreign_keys=[usuario_balancero_id])
    usuario_salida = db.relationship('User', foreign_keys=[usuario_salida_id])
    proceso_desmotado = db.relationship('ProcesoDesmotado', backref='carga', uselist=False)

    @hybrid_property
    def peso_neto(self):
        if self.peso_bruto and self.peso_tara:
            return self.peso_bruto - self.peso_tara
        return 0.0

class ProcesoDesmotado(db.Model):
    """Modelo para registrar los resultados del desmotado."""
    id = db.Column(db.Integer, primary_key=True)
    carga_id = db.Column(db.Integer, db.ForeignKey('carga.id'), nullable=False, unique=True)
    fecha_proceso = db.Column(db.DateTime, default=datetime.utcnow)
    kilos_fibra = db.Column(db.Float, nullable=False)
    kilos_semilla = db.Column(db.Float, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    usuario = db.relationship('User')

