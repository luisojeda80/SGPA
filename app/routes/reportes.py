from flask import Blueprint, render_template
from flask_security import login_required, roles_required
from sqlalchemy import func
from app import db
from app.models.operaciones import Carga, ProcesoDesmotado
from app.models.user import Planta

bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@bp.route('/comparativo-plantas')
@login_required
@roles_required('CasaCentral')
def comparativo_plantas():
    """Muestra un reporte comparativo del rendimiento de todas las plantas."""
    
    # Obtenemos todas las plantas de la base de datos
    plantas = Planta.query.order_by(Planta.nombre).all()
    datos_reporte = []

    for planta in plantas:
        # Total de algodón recibido (peso neto)
        total_neto = db.session.query(func.sum(Carga.peso_neto)).filter(
            Carga.planta_id == planta.id,
            Carga.estado == 'Procesado'
        ).scalar() or 0

        # Total de fibra producida
        total_fibra = db.session.query(func.sum(ProcesoDesmotado.kilos_fibra)).join(Carga).filter(
            Carga.planta_id == planta.id
        ).scalar() or 0
        
        # Rendimiento promedio
        rendimiento = (total_fibra / total_neto * 100) if total_neto > 0 else 0
        
        # Cantidad de lotes procesados
        lotes_procesados = Carga.query.filter(
            Carga.planta_id == planta.id,
            Carga.estado == 'Procesado'
        ).count()

        datos_reporte.append({
            'planta': planta,
            'total_neto': total_neto,
            'total_fibra': total_fibra,
            'rendimiento': rendimiento,
            'lotes_procesados': lotes_procesados
        })

    return render_template('reportes/comparativo_plantas.html', title='Reporte Comparativo de Plantas', datos_reporte=datos_reporte)