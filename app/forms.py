# Agregar esta clase a tu archivo app/forms.py

class LiquidacionForm(FlaskForm):
    """Formulario para generar la liquidación de una carga."""
    precio_kilo_bruto = FloatField(
        'Precio por Kilo Bruto ($)', 
        validators=[
            DataRequired(message='El precio por kilo es obligatorio'),
            NumberRange(min=0.01, message='El precio debe ser mayor a 0')
        ],
        render_kw={"placeholder": "Ej: 200.00", "step": "0.01"}
    )
    
    anticipo = FloatField(
        'Anticipo Recibido ($)', 
        validators=[
            NumberRange(min=0, message='El anticipo no puede ser negativo')
        ],
        default=0.0,
        render_kw={"placeholder": "0.00", "step": "0.01"}
    )
    
    retenciones = FloatField(
        'Retenciones ($)', 
        validators=[
            NumberRange(min=0, message='Las retenciones no pueden ser negativas')
        ],
        default=0.0,
        render_kw={"placeholder": "0.00", "step": "0.01"}
    )
    
    otras_deducciones = FloatField(
        'Otras Deducciones ($)', 
        validators=[
            NumberRange(min=0, message='Las deducciones no pueden ser negativas')
        ],
        default=0.0,
        render_kw={"placeholder": "0.00", "step": "0.01"}
    )
    
    observaciones = TextAreaField(
        'Observaciones',
        render_kw={
            "placeholder": "Observaciones sobre la liquidación (opcional)",
            "rows": 3
        }
    )
    
    submit = SubmitField('Generar Liquidación')