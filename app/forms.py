from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, FloatField, IntegerField, DateField, FieldList, FormField, HiddenField
from wtforms.validators import DataRequired, Length, Email, Optional, NumberRange
from wtforms import ValidationError
from datetime import datetime

# ============================================================================
# FORMULARIOS BÁSICOS (necesarios para recepcion.py)
# ============================================================================

class CargaEntradaForm(FlaskForm):
    """Formulario para registrar la entrada de una nueva carga."""
    productor = SelectField('Productor', coerce=int, validators=[DataRequired()])
    chofer_nombre = StringField('Nombre del Chofer', validators=[DataRequired(), Length(max=150)])
    chofer_dni = StringField('DNI del Chofer', validators=[DataRequired(), Length(min=7, max=10)])
    vehiculo_placa = StringField('Placa del Vehículo', validators=[DataRequired(), Length(min=6, max=10)])
    placa_acoplado = StringField('Placa del Acoplado', validators=[Optional(), Length(min=6, max=10)])
    peso_bruto = FloatField('Peso Bruto (kg)', validators=[DataRequired(message="El peso bruto es obligatorio.")])
    numero_bascula = IntegerField('Número de Báscula', validators=[DataRequired()])
    dtv = StringField('Número de DTE-V', validators=[Optional(), Length(max=50)])
    humedad = FloatField('Humedad (%)', validators=[Optional(), NumberRange(min=0, max=100)])
    observaciones_romaneo = TextAreaField('Observaciones del Romaneo', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Registrar Entrada')

class CargaSalidaForm(FlaskForm):
    """Formulario para registrar la salida de una carga."""
    peso_tara = FloatField('Peso Tara (kg)', validators=[DataRequired(message="El peso tara es obligatorio.")])
    submit = SubmitField('Registrar Salida y Completar')

    def __init__(self, carga, *args, **kwargs):
        super(CargaSalidaForm, self).__init__(*args, **kwargs)
        self.carga = carga

    def validate_peso_tara(self, field):
        if field.data and self.carga and field.data > self.carga.peso_bruto:
            raise ValidationError('El peso tara no puede ser mayor que el peso bruto.')

class ProductorForm(FlaskForm):
    """Formulario para crear y editar Productores."""
    nombre_completo = StringField('Nombre Completo', validators=[DataRequired(message="El nombre es obligatorio."), Length(max=200)])
    cuit = StringField('CUIT', validators=[DataRequired(message="El CUIT es obligatorio."), Length(min=11, max=13)])
    renpa = StringField('RENPA', validators=[Optional(), Length(max=20)])
    telefono = StringField('Teléfono', validators=[Optional(), Length(max=50)])
    email = StringField('Email', validators=[Optional(), Email(message="Email inválido."), Length(max=120)])
    submit = SubmitField('Guardar')

class DesmotadoForm(FlaskForm):
    """Formulario para registrar los resultados del proceso de desmotado."""
    kilos_fibra = FloatField('Kilos de Fibra Producidos', validators=[DataRequired("Este campo es obligatorio."), NumberRange(min=0)])
    kilos_semilla = FloatField('Kilos de Semilla Producidos', validators=[DataRequired("Este campo es obligatorio."), NumberRange(min=0)])
    observaciones = TextAreaField('Observaciones', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Guardar Proceso')

class FardoForm(FlaskForm):
    """Formulario para añadir un nuevo fardo a un proceso."""
    peso = FloatField('Peso del Fardo (kg)', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Añadir Fardo')

class ClasificacionForm(FlaskForm):
    """Formulario para clasificar la calidad de un fardo."""
    grado = SelectField('Grado de Calidad', choices=[('A', 'Grado A'), ('B', 'Grado B'), ('C', 'Grado C'), ('D', 'Grado D')], validators=[DataRequired()])
    longitud_fibra = FloatField('Longitud de Fibra (mm)', validators=[Optional(), NumberRange(min=0)])
    resistencia = FloatField('Resistencia (g/tex)', validators=[Optional(), NumberRange(min=0)])
    micronaire = FloatField('Micronaire', validators=[Optional(), NumberRange(min=0)])
    observaciones = TextAreaField('Observaciones', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Guardar Clasificación')

# ============================================================================
# FORMULARIOS DE LIQUIDACIÓN (los que ya tienes)
# ============================================================================

class PesajeLiquidacionForm(FlaskForm):
    """Formulario para cada pesaje individual en la liquidación."""
    fecha_pesaje = DateField('Fecha Pesaje', validators=[DataRequired()], default=datetime.utcnow)
    peso_bruto = FloatField('Peso Bruto (kg)', validators=[DataRequired(), NumberRange(min=0)])
    peso_tara = FloatField('Peso Tara (kg)', validators=[DataRequired(), NumberRange(min=0)])
    observaciones = StringField('Observaciones', validators=[Optional(), Length(max=200)])

class FardoLiquidacionForm(FlaskForm):
    """Formulario para cada fardo en la liquidación."""
    numero_fardo = IntegerField('N° Fardo', validators=[DataRequired(), NumberRange(min=1)])
    peso = FloatField('Peso (kg)', validators=[DataRequired(), NumberRange(min=0)])
    calidad = SelectField('Calidad', 
                         choices=[('1', 'Calidad 1'), ('2', 'Calidad 2'), ('3', 'Calidad 3')], 
                         validators=[DataRequired()])
    observaciones = StringField('Observaciones', validators=[Optional(), Length(max=200)])

class RangoFardosForm(FlaskForm):
    """Formulario para rangos de fardos."""
    desde_fardo = IntegerField('Desde Fardo N°', validators=[DataRequired(), NumberRange(min=1)])
    hasta_fardo = IntegerField('Hasta Fardo N°', validators=[DataRequired(), NumberRange(min=1)])
    calidad = SelectField('Calidad', 
                         choices=[('1', 'Calidad 1'), ('2', 'Calidad 2'), ('3', 'Calidad 3')], 
                         validators=[DataRequired()])

class LiquidacionCompletaForm(FlaskForm):
    """Formulario completo para liquidación con todos los campos requeridos."""
    
    # 1. Datos obligatorios de la liquidación
    numero_ticket_balanza = StringField('N° Ticket Balanza', 
                                       validators=[DataRequired(), Length(max=20)],
                                       description="Número único generado por el sistema")
    numero_romaneo = StringField('N° Romaneo', 
                                validators=[DataRequired(), Length(max=20)])
    fecha_liquidacion = DateField('Fecha de Liquidación', 
                                 validators=[DataRequired()], 
                                 default=datetime.utcnow)
    productor_id = SelectField('Productor', 
                              coerce=int, 
                              validators=[DataRequired()])
    campo_lote = StringField('Campo / Lote', 
                            validators=[Optional(), Length(max=100)])
    
    # 2. Datos de pesaje (se pueden agregar múltiples)
    algodon_bruto_total = FloatField('Algodón Bruto Total (kg)', 
                                    validators=[DataRequired(), NumberRange(min=0)],
                                    description="Suma total de todos los pesajes")
    fibra_obtenida = FloatField('Fibra Obtenida (kg)', 
                               validators=[DataRequired(), NumberRange(min=0)],
                               description="Peso total de fibra producida")
    semilla_obtenida = FloatField('Semilla Obtenida (kg)', 
                                 validators=[DataRequired(), NumberRange(min=0)],
                                 description="Peso total de semilla producida")
    
    # 3. Cálculo de rendimiento (automático pero editable)
    rinde_porcentaje = FloatField('Rinde (%)', 
                                 validators=[Optional(), NumberRange(min=0, max=100)],
                                 render_kw={'readonly': True})
    
    # 4. Precio por tonelada según calidad
    calidad_algodon = SelectField('Calidad Algodón', 
                                 choices=[('1', 'Calidad 1'), ('2', 'Calidad 2'), ('3', 'Calidad 3')],
                                 validators=[DataRequired()])
    precio_por_tonelada = FloatField('Precio por Tonelada ($)', 
                                    validators=[DataRequired(), NumberRange(min=0)],
                                    description="Precio según calidad seleccionada")
    
    # 5. Gastos asociados
    deuda_semilla = FloatField('Deuda por Semilla ($)', 
                              default=0.0, 
                              validators=[Optional(), NumberRange(min=0)])
    descuento_prestamos = FloatField('Descuento por Préstamos ($)', 
                                    default=0.0, 
                                    validators=[Optional(), NumberRange(min=0)])
    adelantos = FloatField('Adelantos ($)', 
                          default=0.0, 
                          validators=[Optional(), NumberRange(min=0)])
    otros_gastos = FloatField('Otros Gastos ($)', 
                             default=0.0, 
                             validators=[Optional(), NumberRange(min=0)])
    descripcion_otros_gastos = TextAreaField('Descripción Otros Gastos', 
                                           validators=[Optional(), Length(max=500)])
    
    # 6. Forma de pago
    forma_pago = SelectField('Forma de Pago',
                            choices=[
                                ('transferencia', 'Transferencia Bancaria'),
                                ('banco', 'Pago en Banco'), 
                                ('efectivo', 'Efectivo')
                            ],
                            validators=[DataRequired()])
    banco_destino = StringField('Banco Destino', 
                               validators=[Optional(), Length(max=100)])
    cuenta_destino = StringField('Cuenta/CBU Destino', 
                                validators=[Optional(), Length(max=50)])
    
    # 7. Control interno
    numero_orden_pago = StringField('N° Orden de Pago', 
                                   validators=[Optional(), Length(max=20)])
    sucursal_cobro = StringField('Sucursal de Cobro', 
                                validators=[Optional(), Length(max=100)])
    
    # 8. Observaciones generales
    observaciones = TextAreaField('Observaciones Generales', 
                                validators=[Optional(), Length(max=1000)])
    
    submit = SubmitField('Generar Liquidación')
    
    # Campos calculados (solo lectura)
    total_bruto = FloatField('Total Bruto a Liquidar ($)', 
                            validators=[Optional()],
                            render_kw={'readonly': True})
    total_gastos = FloatField('Total Gastos ($)', 
                             validators=[Optional()],
                             render_kw={'readonly': True})
    neto_a_pagar = FloatField('Neto a Pagar ($)', 
                             validators=[Optional()],
                             render_kw={'readonly': True})

class LiquidacionDesdeCargaForm(FlaskForm):
    """Formulario simplificado para crear liquidación desde carga existente."""
    numero_ticket_balanza = StringField('N° Ticket Balanza', 
                                       validators=[DataRequired(), Length(max=20)])
    numero_romaneo = StringField('N° Romaneo', 
                                validators=[DataRequired(), Length(max=20)])
    calidad_algodon = SelectField('Calidad Algodón', 
                                 choices=[('1', 'Calidad 1'), ('2', 'Calidad 2'), ('3', 'Calidad 3')],
                                 validators=[DataRequired()])
    precio_por_tonelada = FloatField('Precio por Tonelada ($)', 
                                    validators=[DataRequired(), NumberRange(min=0)])
    
    # Gastos
    deuda_semilla = FloatField('Deuda por Semilla ($)', default=0.0)
    descuento_prestamos = FloatField('Descuento por Préstamos ($)', default=0.0)
    adelantos = FloatField('Adelantos ($)', default=0.0)
    otros_gastos = FloatField('Otros Gastos ($)', default=0.0)
    descripcion_otros_gastos = TextAreaField('Descripción Otros Gastos')
    
    # Forma de pago
    forma_pago = SelectField('Forma de Pago',
                            choices=[
                                ('transferencia', 'Transferencia Bancaria'),
                                ('banco', 'Pago en Banco'),
                                ('efectivo', 'Efectivo')
                            ],
                            validators=[DataRequired()])
    banco_destino = StringField('Banco Destino')
    cuenta_destino = StringField('Cuenta/CBU Destino')
    
    submit = SubmitField('Crear Liquidación')

class BuscarLiquidacionForm(FlaskForm):
    """Formulario para buscar liquidaciones."""
    numero_ticket_balanza = StringField('N° Ticket Balanza', validators=[Optional()])
    productor_id = SelectField('Productor', coerce=int, validators=[Optional()])
    fecha_desde = DateField('Fecha Desde', validators=[Optional()])
    fecha_hasta = DateField('Fecha Hasta', validators=[Optional()])
    submit = SubmitField('Buscar')

# Mantener el formulario original de liquidación para compatibilidad
class LiquidacionForm(FlaskForm):
    """Formulario para ingresar los datos de la liquidación."""
    precio_kilo_bruto = FloatField('Precio por Kilo de Algodón Bruto ($)', 
                                  validators=[DataRequired(), NumberRange(min=0)])
    anticipo = FloatField('Anticipo Recibido ($)', 
                         default=0.0, 
                         validators=[Optional(), NumberRange(min=0)])
    retenciones = FloatField('Importe de Retenciones ($)', 
                            default=0.0, 
                            validators=[Optional(), NumberRange(min=0)])
    otras_deducciones = FloatField('Otras Deducciones ($)', 
                                  default=0.0, 
                                  validators=[Optional(), NumberRange(min=0)])
    observaciones = TextAreaField('Observaciones', 
                                 validators=[Optional(), Length(max=500)])
    submit = SubmitField('Generar y Guardar Liquidación')