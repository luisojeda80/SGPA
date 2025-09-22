from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Optional

class ProductorForm(FlaskForm):
    """Formulario para crear y editar Productores."""
    nombre_completo = StringField(
        'Nombre Completo',
        validators=[DataRequired(message="El nombre es obligatorio."), Length(max=200)]
    )
    cuit = StringField(
        'CUIT',
        validators=[DataRequired(message="El CUIT es obligatorio."), Length(min=11, max=13)]
    )
    renpa = StringField('RENPA', validators=[Optional(), Length(max=20)])
    telefono = StringField('Teléfono', validators=[Optional(), Length(max=50)])
    email = StringField('Email', validators=[Optional(), Email(message="Email inválido."), Length(max=120)])
    submit = SubmitField('Guardar')
