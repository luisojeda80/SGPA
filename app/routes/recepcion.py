from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_security import login_required, roles_accepted, current_user
from app import db
from app.forms import CargaEntradaForm, CargaSalidaForm
from app.models.operaciones import Carga, Productor, Chofer, Vehiculo
from app.utils.helpers import generar_numero_lote
from datetime import datetime

# Definimos el Blueprint para este módulo
bp = Blueprint('recepcion', __name__, url_prefix='/recepcion')

@bp.route('/nueva_carga', methods=['GET', 'POST'])
@login_required
@roles_accepted('Balancero', 'Administrativo', 'AdminPlanta', 'CasaCentral')
def nueva_carga():
    """Formulario para registrar la entrada de una nueva carga de algodón."""
    form = CargaEntradaForm()
    form.productor.choices = [(p.id, f"{p.nombre_completo} ({p.cuit})") for p in Productor.query.filter_by(activo=True).order_by('nombre_completo')]

    if form.validate_on_submit():
        chofer = Chofer.query.filter_by(dni=form.chofer_dni.data).first()
        if not chofer:
            chofer = Chofer(nombre_completo=form.chofer_nombre.data, dni=form.chofer_dni.data)
            db.session.add(chofer)

        vehiculo = Vehiculo.query.filter_by(placa=form.vehiculo_placa.data).first()
        if not vehiculo:
            vehiculo = Vehiculo(placa=form.vehiculo_placa.data)
            db.session.add(vehiculo)

        lote = generar_numero_lote(current_user.planta.codigo)

        nueva_carga = Carga(
            lote_id=lote,
            planta_id=current_user.planta_id,
            productor_id=form.productor.data,
            chofer=chofer,
            vehiculo=vehiculo,
            peso_bruto=form.peso_bruto.data,
            numero_bascula=form.numero_bascula.data,
            usuario_balancero_id=current_user.id,
            dtv=form.dtv.data,
            humedad=form.humedad.data,
            observaciones_romaneo=form.observaciones_romaneo.data,
            placa_acoplado=form.placa_acoplado.data
        )
        db.session.add(nueva_carga)
        db.session.commit()

        flash(f'Entrada registrada exitosamente. Lote asignado: {lote}', 'success')
        return redirect(url_for('recepcion.listar_cargas'))

    return render_template('recepcion/form_carga.html', title='Registrar Entrada de Carga', form=form)


@bp.route('/registrar_salida/<int:carga_id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('Balancero', 'Administrativo', 'AdminPlanta', 'CasaCentral')
def registrar_salida(carga_id):
    """Formulario para registrar la salida de una carga y calcular el peso neto."""
    carga = Carga.query.get_or_404(carga_id)
    if carga.fecha_salida:
        flash('Esta carga ya tiene registrada una salida.', 'warning')
        return redirect(url_for('recepcion.listar_cargas'))

    # --- LÍNEA CORREGIDA ---
    # Le pasamos el objeto 'carga' al formulario al crearlo.
    form = CargaSalidaForm(carga=carga)
    
    if form.validate_on_submit():
        carga.peso_tara = form.peso_tara.data
        carga.fecha_salida = datetime.utcnow()
        carga.usuario_salida_id = current_user.id
        carga.estado = 'Completado'
        
        db.session.commit()
        flash(f'Salida del lote {carga.lote_id} registrada. Peso neto calculado: {carga.peso_neto:.2f} kg.', 'success')
        return redirect(url_for('recepcion.listar_cargas'))

    return render_template('recepcion/form_salida.html', title=f'Registrar Salida Lote {carga.lote_id}', form=form, carga=carga)


@bp.route('/')
@login_required
def listar_cargas():
    """Muestra una lista paginada de las cargas recibidas."""
    page = request.args.get('page', 1, type=int)

    query = Carga.query
    if not current_user.has_role('CasaCentral'):
        query = query.filter_by(planta_id=current_user.planta_id)

    cargas = query.order_by(Carga.fecha_entrada.desc()).paginate(
        page=page, per_page=10
    )
    return render_template('recepcion/lista_cargas.html', title='Historial de Cargas', cargas=cargas)

