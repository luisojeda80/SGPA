from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_security import login_required, roles_accepted, current_user
from app import db
from app.forms import LiquidacionForm
from app.models.operaciones import Carga, Liquidacion
from app.utils.helpers import generar_numero_liquidacion
from datetime import datetime

bp = Blueprint('liquidacion', __name__, url_prefix='/liquidacion')

@bp.route('/pendientes')
@login_required
@roles_accepted('Administrativo', 'AdminPlanta', 'CasaCentral')
def lotes_pendientes():
    """Muestra los lotes que han sido procesados y están pendientes de liquidación."""
    page = request.args.get('page', 1, type=int)
    
    query = Carga.query.filter(
        Carga.estado == 'Procesado',
        Carga.liquidacion == None
    )

    if not current_user.has_role('CasaCentral'):
        query = query.filter(Carga.planta_id == current_user.planta_id)

    lotes = query.order_by(Carga.fecha_salida.asc()).paginate(page=page, per_page=10)
    
    return render_template('liquidacion/lista_lotes_pendientes.html', title='Lotes Pendientes de Liquidar', lotes=lotes)

@bp.route('/generar/<int:carga_id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('Administrativo', 'AdminPlanta', 'CasaCentral')
def generar_liquidacion(carga_id):
    """Formulario para generar la liquidación de un lote específico."""
    carga = Carga.query.get_or_404(carga_id)
    
    if carga.liquidacion:
        flash('Este lote ya ha sido liquidado.', 'warning')
        return redirect(url_for('liquidacion.lotes_pendientes'))

    form = LiquidacionForm()
    if form.validate_on_submit():
        # --- CÁLCULOS CORREGIDOS ---
        precio_kilo = form.precio_kilo_bruto.data
        total_bruto = carga.peso_neto * precio_kilo
        # Se usan los nuevos nombres de los campos del formulario
        total_a_pagar = total_bruto - form.anticipo_recibido.data - form.importe_retencion.data - form.otras_deducciones.data
        
        numero_liq = generar_numero_liquidacion()

        liq = Liquidacion(
            carga_id=carga.id,
            numero_liquidacion=numero_liq,
            precio_kilo_bruto=precio_kilo,
            total_bruto=total_bruto,
            # Se guardan los datos usando los nombres correctos del modelo
            anticipo=form.anticipo_recibido.data,
            retenciones=form.importe_retencion.data,
            otras_deducciones=form.otras_deducciones.data,
            total_a_pagar=total_a_pagar,
            observaciones=form.observaciones.data, # Asumiendo que quieres añadir un campo de observaciones
            usuario_id=current_user.id
        )
        
        carga.estado = 'Liquidado'
        
        db.session.add(liq)
        db.session.commit()
        
        flash(f'Liquidación {numero_liq} generada exitosamente para el lote {carga.lote_id}.', 'success')
        return redirect(url_for('liquidacion.lotes_pendientes'))

    return render_template('liquidacion/form_liquidacion.html', title=f'Liquidar Lote {carga.lote_id}', form=form, carga=carga)