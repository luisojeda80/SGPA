from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_security import login_required, roles_accepted, current_user
from app import db
from app.forms import FardoForm, ClasificacionForm
from app.models.operaciones import ProcesoDesmotado, Fardo, ClasificacionCalidad, Carga

# Definimos el Blueprint para este módulo
bp = Blueprint('calidad', __name__, url_prefix='/calidad')

@bp.route('/procesos')
@login_required
@roles_accepted('Administrativo', 'AdminPlanta', 'CasaCentral')
def listar_procesos():
    """Muestra una lista de todos los procesos de desmotado completados."""
    page = request.args.get('page', 1, type=int)
    
    query = ProcesoDesmotado.query
    if not current_user.has_role('CasaCentral'):
        query = query.join(Carga).filter(Carga.planta_id == current_user.planta_id)

    procesos = query.order_by(ProcesoDesmotado.fecha_proceso.desc()).paginate(page=page, per_page=10)
    return render_template('calidad/lista_procesos.html', title='Control de Calidad', procesos=procesos)

@bp.route('/proceso/<int:proceso_id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('Administrativo', 'AdminPlanta', 'CasaCentral')
def detalle_proceso(proceso_id):
    """Muestra el detalle de un proceso, sus fardos y permite añadir nuevos."""
    proceso = ProcesoDesmotado.query.get_or_404(proceso_id)
    form = FardoForm()

    if form.validate_on_submit():
        # CORRECCIÓN: Cambiar proceso.carga.planta_id por proceso.id
        siguiente_numero = Fardo.siguiente_numero_fardo(proceso.id)
        
        # CORRECCIÓN: Cambiar proceso_desmotado_id por proceso_id
        nuevo_fardo = Fardo(
            proceso_id=proceso.id,  # ← CAMBIADO
            numero_fardo=siguiente_numero,
            peso=form.peso.data
        )
        db.session.add(nuevo_fardo)
        db.session.commit()
        flash(f'Fardo N° {siguiente_numero} añadido exitosamente.', 'success')
        return redirect(url_for('calidad.detalle_proceso', proceso_id=proceso.id))

    return render_template('calidad/detalle_proceso.html', title=f'Detalle Lote {proceso.carga.lote_id}', proceso=proceso, form=form)


@bp.route('/fardo/<int:fardo_id>/clasificar', methods=['GET', 'POST'])
@login_required
@roles_accepted('Administrativo', 'AdminPlanta', 'CasaCentral')
def clasificar_fardo(fardo_id):
    """Formulario para clasificar la calidad de un fardo."""
    fardo = Fardo.query.get_or_404(fardo_id)
    if fardo.clasificacion:
        flash('Este fardo ya ha sido clasificado.', 'info')
        # Si ya existe, lo mandamos a editar en lugar de crear
        return redirect(url_for('calidad.editar_clasificacion', fardo_id=fardo.id))

    form = ClasificacionForm()
    if form.validate_on_submit():
        nueva_clasificacion = ClasificacionCalidad(
            fardo_id=fardo.id,
            grado=form.grado.data,
            longitud_fibra=form.longitud_fibra.data,
            resistencia=form.resistencia.data,
            micronaire=form.micronaire.data,
            observaciones=form.observaciones.data,
            usuario_id=current_user.id
        )
        db.session.add(nueva_clasificacion)
        db.session.commit()
        flash(f'Clasificación del fardo N° {fardo.numero_fardo} guardada.', 'success')
        # CORRECCIÓN: Cambiar proceso_desmotado_id por proceso_id
        return redirect(url_for('calidad.detalle_proceso', proceso_id=fardo.proceso_id))

    return render_template('calidad/form_clasificacion.html', title=f'Clasificar Fardo N° {fardo.numero_fardo}', form=form, fardo=fardo)

@bp.route('/fardo/<int:fardo_id>/editar_clasificacion', methods=['GET', 'POST'])
@login_required
@roles_accepted('Administrativo', 'AdminPlanta', 'CasaCentral')
def editar_clasificacion(fardo_id):
    """Formulario para editar la clasificación de un fardo."""
    fardo = Fardo.query.get_or_404(fardo_id)
    clasificacion = fardo.clasificacion
    if not clasificacion:
        return redirect(url_for('calidad.clasificar_fardo', fardo_id=fardo.id))
    
    form = ClasificacionForm(obj=clasificacion)
    if form.validate_on_submit():
        clasificacion.grado = form.grado.data
        clasificacion.longitud_fibra = form.longitud_fibra.data
        clasificacion.resistencia = form.resistencia.data
        clasificacion.micronaire = form.micronaire.data
        clasificacion.observaciones = form.observaciones.data
        db.session.commit()
        flash(f'Clasificación del fardo N° {fardo.numero_fardo} actualizada.', 'success')
        # CORRECCIÓN: Cambiar proceso_desmotado_id por proceso_id
        return redirect(url_for('calidad.detalle_proceso', proceso_id=fardo.proceso_id))

    return render_template('calidad/form_clasificacion.html', title=f'Editar Clasificación Fardo N° {fardo.numero_fardo}', form=form, fardo=fardo)