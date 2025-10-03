from app import db
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
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
    
    # --- RELACIÓN CORREGIDA ---
    liquidacion_asociada = db.relationship('Liquidacion', backref='carga_origen', uselist=False)

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
    observaciones = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    operario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relaciones
    usuario = db.relationship('User', foreign_keys=[usuario_id])
    operario = db.relationship('User', foreign_keys=[operario_id])
    
    fardos = db.relationship('Fardo', backref='proceso_desmotado', lazy='dynamic')

    @hybrid_property
    def rendimiento(self):
        if self.kilos_fibra and self.carga.peso_neto > 0:
            return (self.kilos_fibra / self.carga.peso_neto) * 100
        return 0.0

class Fardo(db.Model):
    """Modelo para los fardos de fibra producidos."""
    id = db.Column(db.Integer, primary_key=True)
    proceso_id = db.Column(db.Integer, db.ForeignKey('proceso_desmotado.id'), nullable=False)
    numero_fardo = db.Column(db.Integer, nullable=False)
    peso = db.Column(db.Float, nullable=False)
    clasificacion = db.relationship('ClasificacionCalidad', backref='fardo', uselist=False)

class ClasificacionCalidad(db.Model):
    """Modelo para la clasificación de calidad de un fardo."""
    id = db.Column(db.Integer, primary_key=True)
    fardo_id = db.Column(db.Integer, db.ForeignKey('fardo.id'), nullable=False, unique=True)
    grado = db.Column(db.String(1), nullable=False) # A, B, C, D
    longitud_fibra = db.Column(db.Float)
    resistencia = db.Column(db.Float)
    micronaire = db.Column(db.Float)
    observaciones = db.Column(db.Text)
    fecha_clasificacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    usuario = db.relationship('User')

class Liquidacion(db.Model):
    """Modelo ampliado para liquidación de algodón."""
    id = db.Column(db.Integer, primary_key=True)
    
    # 1. Datos obligatorios de la liquidación
    numero_ticket_balanza = db.Column(db.String(20), unique=True, nullable=False)
    numero_romaneo = db.Column(db.String(20), nullable=False)
    fecha_liquidacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    productor_id = db.Column(db.Integer, db.ForeignKey('productor.id'), nullable=False)
    campo_lote = db.Column(db.String(100))
    
    # 2. Relación con carga (opcional - puede ser independiente)
    carga_id = db.Column(db.Integer, db.ForeignKey('carga.id'))
    
    # 3. Parámetros de cálculo
    algodon_bruto_total = db.Column(db.Float, nullable=False)  # kg
    fibra_obtenida = db.Column(db.Float, nullable=False)       # kg
    semilla_obtenida = db.Column(db.Float, nullable=False)     # kg
    
    # 4. Precios y calidad
    calidad_algodon = db.Column(db.String(1), nullable=False)  # 1, 2, 3
    precio_por_tonelada = db.Column(db.Float, nullable=False)
    
    # 5. Gastos asociados
    deuda_semilla = db.Column(db.Float, default=0.0)
    descuento_prestamos = db.Column(db.Float, default=0.0)
    adelantos = db.Column(db.Float, default=0.0)
    otros_gastos = db.Column(db.Float, default=0.0)
    descripcion_otros_gastos = db.Column(db.Text)
    
    # 6. Forma de pago
    forma_pago = db.Column(db.String(20), nullable=False)  # transferencia, banco, efectivo
    banco_destino = db.Column(db.String(100))
    cuenta_destino = db.Column(db.String(50))
    
    # 7. Control interno
    numero_orden_pago = db.Column(db.String(20))
    sucursal_cobro = db.Column(db.String(100))
    observaciones = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relaciones CORREGIDAS
    productor = db.relationship('Productor')
    # La relación con carga se maneja a través de carga_id
    usuario = db.relationship('User')
    pesajes = db.relationship('PesajeLiquidacion', backref='liquidacion_padre', lazy='dynamic')
    fardos = db.relationship('FardoLiquidacion', backref='liquidacion_padre', lazy='dynamic')
    
    # Propiedades calculadas
    @hybrid_property
    def rinde_porcentaje(self):
        if self.algodon_bruto_total > 0:
            return (self.fibra_obtenida / self.algodon_bruto_total) * 100
        return 0.0
    
    @hybrid_property
    def total_bruto(self):
        return (self.fibra_obtenida / 1000) * self.precio_por_tonelada
    
    @hybrid_property
    def total_gastos(self):
        return (self.deuda_semilla + self.descuento_prestamos + 
                self.adelantos + self.otros_gastos)
    
    @hybrid_property
    def neto_a_pagar(self):
        return self.total_bruto - self.total_gastos

class PesajeLiquidacion(db.Model):
    """Modelo para múltiples pesajes en una liquidación."""
    id = db.Column(db.Integer, primary_key=True)
    liquidacion_id = db.Column(db.Integer, db.ForeignKey('liquidacion.id'), nullable=False)
    fecha_pesaje = db.Column(db.DateTime, nullable=False)
    peso_bruto = db.Column(db.Float, nullable=False)
    peso_tara = db.Column(db.Float, nullable=False)
    observaciones = db.Column(db.Text)
    
    @hybrid_property
    def peso_neto(self):
        return self.peso_bruto - self.peso_tara

class FardoLiquidacion(db.Model):
    """Modelo para los fardos en la liquidación."""
    id = db.Column(db.Integer, primary_key=True)
    liquidacion_id = db.Column(db.Integer, db.ForeignKey('liquidacion.id'), nullable=False)
    numero_fardo = db.Column(db.Integer, nullable=False)
    peso = db.Column(db.Float, nullable=False)
    calidad = db.Column(db.String(1), nullable=False)  # 1, 2, 3
    observaciones = db.Column(db.Text)