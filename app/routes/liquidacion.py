from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_security import login_required, roles_accepted, current_user
from app import db
from app.forms import LiquidacionForm
from app.models.operaciones import Carga, Liquidacion
from app.utils.helpers import generar_numero_liquidacion # Asumimos que crearemos esta función

bp = Blueprint('liquidacion', __name__, url_prefix='/liquidacion')

@bp.route('/pendientes')
@login_required
@roles_accepted('Administrativo', 'AdminPlanta', 'CasaCentral')
def lotes_pendientes():
    """Muestra los lotes que han sido procesados y están listos para la liquidación."""
    page = request.args.get('page', 1, type=int)
    
    query = Carga.query.filter(
        Carga.estado == 'Procesado',
        Carga.liquidacion == None # Filtramos solo los que no tienen liquidación
    )

    if not current_user.has_role('CasaCentral'):
        query = query.filter(Carga.planta_id == current_user.planta_id)

    lotes = query.order_by(Carga.fecha_salida.asc()).paginate(page=page, per_page=10)
    
    return render_template('liquidacion/lista_lotes_pendientes.html', title='Lotes Pendientes de Liquidación', lotes=lotes)


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
        # Cálculos de la liquidación
        precio_kilo = form.precio_kilo_bruto.data
        total_bruto = carga.peso_neto * precio_kilo
        total_deducciones = (form.anticipo_recibido.data or 0) + \
                            (form.importe_retencion.data or 0) + \
                            (form.otras_deducciones.data or 0)
        total_a_cobrar = total_bruto - total_deducciones

        nueva_liquidacion = Liquidacion(
            carga_id=carga.id,
            numero_liquidacion=generar_numero_liquidacion(current_user.planta.codigo),
            precio_kilo_bruto=precio_kilo,
            total_liquidacion_bruta=total_bruto,
            anticipo_recibido=form.anticipo_recibido.data,
            importe_retencion=form.importe_retencion.data,
            otras_deducciones=form.otras_deducciones.data,
            total_a_cobrar=total_a_cobrar,
            usuario_id=current_user.id
        )
        
        carga.estado = 'Liquidado'
        db.session.add(nueva_liquidacion)
        db.session.commit()
        
        flash(f'Liquidación para el lote {carga.lote_id} generada exitosamente.', 'success')
        # Redirigir a una futura vista de detalle de la liquidación
        return redirect(url_for('liquidacion.lotes_pendientes'))

    return render_template('liquidacion/form_liquidacion.html', title=f'Generar Liquidación para Lote {carga.lote_id}', form=form, carga=carga)