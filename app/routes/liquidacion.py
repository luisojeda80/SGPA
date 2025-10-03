from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_security import login_required, roles_accepted, current_user
from app import db
from app.forms import LiquidacionForm, LiquidacionCompletaForm, LiquidacionDesdeCargaForm, BuscarLiquidacionForm
from app.models.operaciones import Carga, ProcesoDesmotado, Liquidacion, Productor
from datetime import datetime

bp = Blueprint('liquidacion', __name__, url_prefix='/liquidacion')

# ============================================================================
# RUTAS EXISTENTES (mantener compatibilidad)
# ============================================================================

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
        Carga.liquidacion_asociada == None  # ← CAMBIADO AQUÍ
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
    """Formulario para generar la liquidación de un lote específico (versión simple)."""
    carga = Carga.query.get_or_404(carga_id)
    
    # Verificar que el lote esté procesado
    if not carga.proceso_desmotado:
        flash('Este lote no ha sido procesado aún.', 'error')
        return redirect(url_for('liquidacion.lotes_pendientes'))
    
    # Verificar que no esté ya liquidado
    if carga.liquidacion_asociada:  # ← CAMBIADO AQUÍ
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
    
    query = Liquidacion.query
    
    # Si no es Casa Central, filtrar por planta
    if not current_user.has_role('CasaCentral'):
        # Usar join a través de carga_id en lugar de la relación directa
        query = query.join(Carga, Liquidacion.carga_id == Carga.id).filter(Carga.planta_id == current_user.planta_id)
    
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
    if not current_user.has_role('CasaCentral') and liquidacion.carga_origen.planta_id != current_user.planta_id:  # ← CAMBIADO AQUÍ
        flash('No tiene permisos para ver esta liquidación.', 'error')
        return redirect(url_for('liquidacion.historial_liquidaciones'))
    
    return render_template('liquidacion/detalle.html', 
                         title=f'Liquidación {liquidacion.numero_liquidacion}', 
                         liquidacion=liquidacion)

# ============================================================================
# NUEVAS RUTAS (sistema completo)
# ============================================================================

@bp.route('/')
@login_required
@roles_accepted('Administrativo', 'AdminPlanta', 'CasaCentral')
def listar():
    """Listar todas las liquidaciones (nueva versión completa)."""
    page = request.args.get('page', 1, type=int)
    form_busqueda = BuscarLiquidacionForm()
    
    # Configurar choices de productores
    form_busqueda.productor_id.choices = [(0, 'Todos los productores')] + [
        (p.id, p.nombre_completo) for p in Productor.query.filter_by(activo=True).all()
    ]
    
    query = Liquidacion.query
    
    # Aplicar filtros si existen
    if request.args.get('numero_ticket_balanza'):
        query = query.filter(Liquidacion.numero_ticket_balanza.contains(request.args['numero_ticket_balanza']))
    if request.args.get('productor_id') and request.args['productor_id'] != '0':
        query = query.filter(Liquidacion.productor_id == request.args['productor_id'])
    
    liquidaciones = query.order_by(Liquidacion.fecha_liquidacion.desc()).paginate(
        page=page, per_page=10
    )
    
    return render_template('liquidacion/lista.html', 
                         liquidaciones=liquidaciones, 
                         form_busqueda=form_busqueda)

@bp.route('/nueva', methods=['GET', 'POST'])
@login_required
@roles_accepted('Administrativo', 'AdminPlanta', 'CasaCentral')
def nueva():
    """Crear nueva liquidación completa (independiente de carga)."""
    form = LiquidacionCompletaForm()
    
    # Cargar choices de productores
    form.productor_id.choices = [(p.id, p.nombre_completo) for p in Productor.query.filter_by(activo=True).all()]
    
    if form.validate_on_submit():
        try:
            # Calcular rinde automáticamente
            rinde = (form.fibra_obtenida.data / form.algodon_bruto_total.data) * 100 if form.algodon_bruto_total.data > 0 else 0
            
            # Generar número de liquidación único
            numero_liquidacion = f"LIQ-{datetime.now().strftime('%Y%m%d')}-{Liquidacion.query.count() + 1:04d}"
            
            liquidacion = Liquidacion(
                # Datos obligatorios
                numero_ticket_balanza=form.numero_ticket_balanza.data,
                numero_romaneo=form.numero_romaneo.data,
                fecha_liquidacion=form.fecha_liquidacion.data,
                productor_id=form.productor_id.data,
                campo_lote=form.campo_lote.data,
                numero_liquidacion=numero_liquidacion,
                
                # Parámetros de cálculo
                algodon_bruto_total=form.algodon_bruto_total.data,
                fibra_obtenida=form.fibra_obtenida.data,
                semilla_obtenida=form.semilla_obtenida.data,
                
                # Precios y calidad
                calidad_algodon=form.calidad_algodon.data,
                precio_por_tonelada=form.precio_por_tonelada.data,
                
                # Gastos
                deuda_semilla=form.deuda_semilla.data,
                descuento_prestamos=form.descuento_prestamos.data,
                adelantos=form.adelantos.data,
                otros_gastos=form.otros_gastos.data,
                descripcion_otros_gastos=form.descripcion_otros_gastos.data,
                
                # Forma de pago
                forma_pago=form.forma_pago.data,
                banco_destino=form.banco_destino.data,
                cuenta_destino=form.cuenta_destino.data,
                
                # Control
                numero_orden_pago=form.numero_orden_pago.data,
                sucursal_cobro=form.sucursal_cobro.data,
                observaciones=form.observaciones.data,
                usuario_id=current_user.id
            )
            
            db.session.add(liquidacion)
            db.session.commit()
            
            flash(f'Liquidación {liquidacion.numero_ticket_balanza} creada exitosamente', 'success')
            return redirect(url_for('liquidacion.detalle_completa', id=liquidacion.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear liquidación: {str(e)}', 'error')
    
    return render_template('liquidacion/nueva.html', form=form)

@bp.route('/desde-carga/<int:carga_id>', methods=['GET', 'POST'])
@login_required
def desde_carga(carga_id):
    """Crear liquidación automáticamente desde una carga procesada."""
    carga = Carga.query.get_or_404(carga_id)
    
    if not carga.proceso_desmotado:
        flash('La carga debe estar procesada antes de liquidar', 'warning')
        return redirect(url_for('desmotado.lotes_pendientes'))
    
    form = LiquidacionDesdeCargaForm()
    
    if form.validate_on_submit():
        try:
            # Generar número de liquidación único
            numero_liquidacion = f"LIQ-{datetime.now().strftime('%Y%m%d')}-{carga.id:04d}"
            
            liquidacion = Liquidacion(
                numero_ticket_balanza=form.numero_ticket_balanza.data,
                numero_romaneo=form.numero_romaneo.data,
                fecha_liquidacion=datetime.utcnow(),
                productor_id=carga.productor_id,
                campo_lote=carga.lote_id,
                carga_id=carga.id,
                numero_liquidacion=numero_liquidacion,
                
                # Datos del desmotado
                algodon_bruto_total=carga.peso_neto,
                fibra_obtenida=carga.proceso_desmotado.kilos_fibra,
                semilla_obtenida=carga.proceso_desmotado.kilos_semilla,
                
                # Datos del formulario
                calidad_algodon=form.calidad_algodon.data,
                precio_por_tonelada=form.precio_por_tonelada.data,
                
                # Gastos
                deuda_semilla=form.deuda_semilla.data,
                descuento_prestamos=form.descuento_prestamos.data,
                adelantos=form.adelantos.data,
                otros_gastos=form.otros_gastos.data,
                descripcion_otros_gastos=form.descripcion_otros_gastos.data,
                
                # Forma de pago
                forma_pago=form.forma_pago.data,
                banco_destino=form.banco_destino.data,
                cuenta_destino=form.cuenta_destino.data,
                
                usuario_id=current_user.id
            )
            
            # Cambiar estado de la carga
            carga.estado = 'Liquidado'
            
            db.session.add(liquidacion)
            db.session.commit()
            
            flash('Liquidación creada desde carga procesada', 'success')
            return redirect(url_for('liquidacion.detalle_completa', id=liquidacion.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear liquidación: {str(e)}', 'error')
    
    # Valores por defecto
    form.numero_ticket_balanza.data = f"TB-{carga.lote_id}"
    form.numero_romaneo.data = f"RM-{carga.lote_id}"
    
    return render_template('liquidacion/desde_carga.html', form=form, carga=carga)

@bp.route('/completa/<int:id>')
@login_required
def detalle_completa(id):
    """Ver detalle de liquidación completa."""
    liquidacion = Liquidacion.query.get_or_404(id)
    return render_template('liquidacion/detalle_completo.html', liquidacion=liquidacion)

@bp.route('/calcular', methods=['POST'])
@login_required
def calcular():
    """Endpoint para cálculos automáticos."""
    data = request.get_json()
    
    algodon_bruto = data.get('algodon_bruto', 0)
    fibra_obtenida = data.get('fibra_obtenida', 0)
    precio_tonelada = data.get('precio_tonelada', 0)
    
    resultados = {}
    
    # Calcular rinde
    if algodon_bruto > 0:
        rinde = (fibra_obtenida / algodon_bruto) * 100
        resultados['rinde'] = round(rinde, 2)
        
        # Sugerir calidad según rinde
        if rinde >= 33:
            resultados['calidad_sugerida'] = '2'
            resultados['mensaje_calidad'] = 'Rinde ≥33% - Calidad 2 recomendada'
        else:
            resultados['calidad_sugerida'] = '3'
            resultados['mensaje_calidad'] = 'Rinde <33% - Calidad 3 recomendada'
    
    # Calcular total bruto
    if fibra_obtenida > 0 and precio_tonelada > 0:
        total_bruto = (fibra_obtenida / 1000) * precio_tonelada
        resultados['total_bruto'] = round(total_bruto, 2)
    
    return jsonify(resultados)