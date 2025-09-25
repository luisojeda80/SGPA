from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_security import login_required, roles_accepted, current_user
from app import db
from app.forms import LiquidacionForm
from app.models.operaciones import Carga, ProcesoDesmotado, Liquidacion
from datetime import datetime

bp = Blueprint('liquidacion', __name__, url_prefix='/liquidacion')

@bp.route('/pendientes')
@login_required
@roles_accepted('Administrativo', 'AdminPlanta', 'CasaCentral')
def lotes_pendientes():
    """Muestra los lotes que han sido procesados y están pendientes de liquidar."""
    page = request.args.get('page', 1, type=int)
    
    # Solo mostrar lotes que han sido procesados (desmotados) pero no liquidados
    query = Carga.query.filter(
        Carga.estado == 'Procesado',
        Carga.proceso_desmotado != None,
        Carga.liquidacion == None
    )
    
    # Si no es Casa Central, filtrar por planta
    if not current_user.has_role('CasaCentral'):
        query = query.filter(Carga.planta_id == current_user.planta_id)
    
    lotes = query.order_by(Carga.fecha_salida.asc()).paginate(page=page, per_page=10)
    
    return render_template('liquidacion/lotes_pendientes.html', 
                         title='Lotes Pendientes de Liquidar', lotes=lotes)

@bp.route('/generar/<int:carga_id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('Administrativo', 'AdminPlanta', 'CasaCentral')
def generar_liquidacion(carga_id):
    """Formulario para generar la liquidación de un lote específico."""
    carga = Carga.query.get_or_404(carga_id)
    
    # Verificar que el lote esté procesado
    if not carga.proceso_desmotado:
        flash('Este lote no ha sido procesado aún.', 'error')
        return redirect(url_for('liquidacion.lotes_pendientes'))
    
    # Verificar que no esté ya liquidado
    if carga.liquidacion:
        flash('Este lote ya ha sido liquidado.', 'warning')
        return redirect(url_for('liquidacion.lotes_pendientes'))
    
    form = LiquidacionForm()
    
    if form.validate_on_submit():
        # Generar número de liquidación único
        numero_liquidacion = f"LIQ-{datetime.now().strftime('%Y%m%d')}-{carga.id:04d}"
        
        # Calcular totales
        total_bruto = form.precio_kilo_bruto.data * carga.peso_neto
        total_a_pagar = total_bruto - form.anticipo.data - form.retenciones.data - form.otras_deducciones.data
        
        liquidacion = Liquidacion(
            carga_id=carga.id,
            numero_liquidacion=numero_liquidacion,
            precio_kilo_bruto=form.precio_kilo_bruto.data,
            total_bruto=total_bruto,
            anticipo=form.anticipo.data,
            retenciones=form.retenciones.data,
            otras_deducciones=form.otras_deducciones.data,
            total_a_pagar=total_a_pagar,
            observaciones=form.observaciones.data,
            usuario_id=current_user.id
        )
        
        # Cambiar estado del lote
        carga.estado = 'Liquidado'
        
        db.session.add(liquidacion)
        db.session.commit()
        
        flash(f'La liquidación {numero_liquidacion} ha sido generada exitosamente.', 'success')
        return redirect(url_for('liquidacion.lotes_pendientes'))
    
    # Pre-llenar el formulario con datos calculados
    if request.method == 'GET':
        # Precio sugerido (puedes ajustarlo según tu lógica de negocio)
        form.precio_kilo_bruto.data = 200.0  # Ejemplo: $200 por kg
    
    return render_template('liquidacion/form_liquidacion.html', 
                         title=f'Liquidar Lote {carga.lote_id}', 
                         form=form, carga=carga)

@bp.route('/historial')
@login_required
@roles_accepted('Administrativo', 'AdminPlanta', 'CasaCentral')
def historial_liquidaciones():
    """Muestra el historial de liquidaciones realizadas."""
    page = request.args.get('page', 1, type=int)
    
    query = Liquidacion.query.join(Carga)
    
    # Si no es Casa Central, filtrar por planta
    if not current_user.has_role('CasaCentral'):
        query = query.filter(Carga.planta_id == current_user.planta_id)
    
    liquidaciones = query.order_by(Liquidacion.fecha_liquidacion.desc()).paginate(page=page, per_page=15)
    
    return render_template('liquidacion/historial.html', 
                         title='Historial de Liquidaciones', liquidaciones=liquidaciones)

@bp.route('/detalle/<int:liquidacion_id>')
@login_required
@roles_accepted('Administrativo', 'AdminPlanta', 'CasaCentral')
def detalle_liquidacion(liquidacion_id):
    """Muestra el detalle de una liquidación específica."""
    liquidacion = Liquidacion.query.get_or_404(liquidacion_id)
    
    # Verificar permisos por planta
    if not current_user.has_role('CasaCentral') and liquidacion.carga.planta_id != current_user.planta_id:
        flash('No tiene permisos para ver esta liquidación.', 'error')
        return redirect(url_for('liquidacion.historial_liquidaciones'))
    
    return render_template('liquidacion/detalle.html', 
                         title=f'Liquidación {liquidacion.numero_liquidacion}', 
                         liquidacion=liquidacion)