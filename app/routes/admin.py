from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_security import login_required, roles_accepted, current_user
from app import db
from app.forms import ProductorForm
from app.models.operaciones import Productor

# Usamos un prefijo de URL para todas las rutas de este blueprint
bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/productores')
@login_required
@roles_accepted('Administrativo', 'AdminPlanta', 'CasaCentral')
def listar_productores():
    """Muestra una lista paginada de productores."""
    page = request.args.get('page', 1, type=int)
    productores = Productor.query.order_by(Productor.nombre_completo).paginate(
        page=page, per_page=10
    )
    return render_template('admin/lista_productores.html', title='Gestión de Productores', productores=productores)

@bp.route('/productor/nuevo', methods=['GET', 'POST'])
@login_required
@roles_accepted('Administrativo', 'AdminPlanta', 'CasaCentral')
def nuevo_productor():
    """Formulario para crear un nuevo productor."""
    form = ProductorForm()
    if form.validate_on_submit():
        nuevo = Productor(
            nombre_completo=form.nombre_completo.data,
            cuit=form.cuit.data,
            renpa=form.renpa.data,
            telefono=form.telefono.data,
            email=form.email.data
        )
        db.session.add(nuevo)
        db.session.commit()
        flash('Productor creado exitosamente.', 'success')
        return redirect(url_for('admin.listar_productores'))
    return render_template('admin/form_productor.html', title='Nuevo Productor', form=form)

@bp.route('/productor/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_accepted('Administrativo', 'AdminPlanta', 'CasaCentral')
def editar_productor(id):
    """Formulario para editar un productor existente."""
    productor = Productor.query.get_or_404(id)
    form = ProductorForm(obj=productor)
    if form.validate_on_submit():
        productor.nombre_completo = form.nombre_completo.data
        productor.cuit = form.cuit.data
        productor.renpa = form.renpa.data
        productor.telefono = form.telefono.data
        productor.email = form.email.data
        db.session.commit()
        flash('Productor actualizado exitosamente.', 'success')
        return redirect(url_for('admin.listar_productores'))
    return render_template('admin/form_productor.html', title='Editar Productor', form=form)

# --- NUEVA RUTA AÑADIDA ---
@bp.route('/productor/toggle_activo/<int:id>', methods=['POST'])
@login_required
@roles_accepted('Administrativo', 'AdminPlanta', 'CasaCentral')
def toggle_productor_activo(id):
    """Cambia el estado de un productor (activo/inactivo)."""
    productor = Productor.query.get_or_404(id)
    productor.activo = not productor.activo
    db.session.commit()
    estado = "activado" if productor.activo else "desactivado"
    flash(f'El productor "{productor.nombre_completo}" ha sido {estado}.', 'success')
    return redirect(url_for('admin.listar_productores'))