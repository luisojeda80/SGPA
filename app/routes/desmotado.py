from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_security import login_required, roles_accepted, current_user
from app import db
from app.forms import DesmotadoForm
from app.models.operaciones import Carga, ProcesoDesmotado

bp = Blueprint('desmotado', __name__, url_prefix='/desmotado')

@bp.route('/pendientes')
@login_required
@roles_accepted('Administrativo', 'AdminPlanta', 'CasaCentral')
def lotes_pendientes():
    """Muestra los lotes que han completado el pesaje y están pendientes de desmotar."""
    page = request.args.get('page', 1, type=int)
    
    query = Carga.query.filter(
        Carga.estado == 'Completado',
        Carga.proceso_desmotado == None
    )

    if not current_user.has_role('CasaCentral'):
        query = query.filter(Carga.planta_id == current_user.planta_id)

    lotes = query.order_by(Carga.fecha_salida.asc()).paginate(page=page, per_page=10)
    
    return render_template('desmotado/lista_lotes_pendientes.html', title='Lotes Pendientes de Desmotar', lotes=lotes)


@bp.route('/procesar/<int:carga_id>', methods=['GET', 'POST'])
@login_required
# --- LÍNEA CORREGIDA: Se añade 'CasaCentral' a los roles permitidos ---
@roles_accepted('Administrativo', 'AdminPlanta', 'CasaCentral')
def registrar_proceso(carga_id):
    """Formulario para registrar el resultado del desmotado de un lote específico."""
    carga = Carga.query.get_or_404(carga_id)
    
    if carga.proceso_desmotado:
        flash('Este lote ya ha sido procesado.', 'warning')
        return redirect(url_for('desmotado.lotes_pendientes'))

    form = DesmotadoForm()
    if form.validate_on_submit():
        proceso = ProcesoDesmotado(
            carga_id=carga.id,
            kilos_fibra=form.kilos_fibra.data,
            kilos_semilla=form.kilos_semilla.data,
            observaciones=form.observaciones.data,
            usuario_id=current_user.id
        )
        carga.estado = 'Procesado'
        
        db.session.add(proceso)
        db.session.commit()
        
        flash(f'El lote {carga.lote_id} ha sido procesado exitosamente.', 'success')
        return redirect(url_for('desmotado.lotes_pendientes'))

    return render_template('desmotado/form_desmotado.html', title=f'Procesar Lote {carga.lote_id}', form=form, carga=carga)