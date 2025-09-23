from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Email, Optional, NumberRange
from wtforms import ValidationError

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

class LiquidacionForm(FlaskForm):
    """Formulario para ingresar los datos de la liquidación."""
    precio_kilo_bruto = FloatField('Precio por Kilo de Algodón Bruto ($)', validators=[DataRequired(), NumberRange(min=0)])
    anticipo_recibido = FloatField('Anticipo Recibido ($)', validators=[Optional(), NumberRange(min=0)])
    importe_retencion = FloatField('Importe de Retención ($)', validators=[Optional(), NumberRange(min=0)])
    otras_deducciones = FloatField('Otras Deducciones ($)', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Generar y Guardar Liquidación')