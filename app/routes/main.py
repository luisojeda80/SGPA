from flask import Blueprint, render_template
from flask_security import login_required, current_user
from sqlalchemy import func, case
from app import db
from app.models.operaciones import Carga, Productor, ProcesoDesmotado
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    """
    Página principal o Dashboard.
    Renderiza una plantilla diferente según el rol del usuario actual.
    """
    # --- LÍNEA DE DEPURACIÓN AÑADIDA ---
    # Imprime los roles del usuario actual en la terminal para verificar.
    print(f"DEBUG: Usuario '{current_user.email}' tiene los roles: {[role.name for role in current_user.roles]}")

    if current_user.has_role('CasaCentral'):
        # --- KPIs para el Dashboard Corporativo ---
        hoy = datetime.utcnow()
        hace_30_dias = hoy - timedelta(days=30)

        # Producción total de fibra en los últimos 30 días
        produccion_total = db.session.query(func.sum(ProcesoDesmotado.kilos_fibra)).filter(
            ProcesoDesmotado.fecha_proceso >= hace_30_dias
        ).scalar() or 0

        # Cantidad de productores activos
        productores_activos = Productor.query.filter_by(activo=True).count()

        # Rendimiento promedio ponderado
        total_fibra = db.session.query(func.sum(ProcesoDesmotado.kilos_fibra)).scalar() or 0
        total_neto = db.session.query(func.sum(Carga.peso_neto)).join(ProcesoDesmotado).scalar() or 0
        rendimiento_promedio = (total_fibra / total_neto * 100) if total_neto > 0 else 0

        kpis = {
            'produccion_total': f"{produccion_total / 1000:.2f} Ton", # Convertir a toneladas
            'productores_activos': productores_activos,
            'rendimiento_promedio': f"{rendimiento_promedio:.2f}%"
        }
        return render_template('dashboard_central.html', title='Dashboard Corporativo', kpis=kpis)

    else:
        # Dashboard para Balancero y Administrativo
        return render_template('dashboard_operario.html', title='Dashboard de Operaciones')