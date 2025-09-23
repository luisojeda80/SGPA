from flask import Blueprint, render_template
from flask_security import login_required, roles_required
from app import db
from app.models.operaciones import Carga, ProcesoDesmotado, Planta
from sqlalchemy import func

bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@bp.route('/comparativo_plantas')
@login_required
@roles_required('CasaCentral')
def comparativo_plantas():
    """
    Muestra un reporte comparativo del rendimiento entre todas las plantas.
    """
    # Subconsulta para obtener el peso neto total por planta
    subquery_neto = db.session.query(
        Carga.planta_id,
        func.sum(Carga.peso_neto).label('total_neto')
    ).filter(Carga.peso_neto != None).group_by(Carga.planta_id).subquery()

    # Subconsulta para obtener la fibra total producida por planta
    subquery_fibra = db.session.query(
        Carga.planta_id,
        func.sum(ProcesoDesmotado.kilos_fibra).label('total_fibra')
    ).join(ProcesoDesmotado).group_by(Carga.planta_id).subquery()

    # Consulta principal que une los resultados con la información de la planta
    datos_plantas = db.session.query(
        Planta,
        subquery_neto.c.total_neto,
        subquery_fibra.c.total_fibra
    ).outerjoin(subquery_neto, Planta.id == subquery_neto.c.planta_id)\
     .outerjoin(subquery_fibra, Planta.id == subquery_fibra.c.planta_id)\
     .order_by(Planta.nombre).all()
    
    # Procesar los datos para la plantilla
    reporte = []
    for planta, total_neto, total_fibra in datos_plantas:
        total_neto = total_neto or 0
        total_fibra = total_fibra or 0
        rendimiento = (total_fibra / total_neto * 100) if total_neto > 0 else 0
        reporte.append({
            'planta': planta,
            'total_neto': total_neto,
            'total_fibra': total_fibra,
            'rendimiento': rendimiento
        })

    return render_template('reportes/comparativo_plantas.html', title='Reporte Comparativo de Plantas', reporte=reporte)
