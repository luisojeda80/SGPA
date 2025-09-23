# C:/SGPA/app/utils/helpers.py
from app.models.operaciones import Carga, Liquidacion
from datetime import datetime
import qrcode
import os

def generar_numero_lote(planta_codigo):
    """
    Genera un número de lote único y consecutivo para una planta.
    Formato: [CODIGO_PLANTA]-[AÑO]-[NUMERO_SECUENCIAL]
    Ejemplo: P01-2025-000123
    """
    from app import db # Importar aquí para evitar importación circular
    current_year = datetime.now().year
    
    last_lote_str = db.session.query(db.func.max(Carga.lote_id)).filter(
        Carga.lote_id.like(f'{planta_codigo}-{current_year}-%')
    ).scalar()
    
    new_seq = 1
    if last_lote_str:
        last_seq = int(last_lote_str.split('-')[-1])
        new_seq = last_seq + 1
        
    return f"{planta_codigo}-{current_year}-{new_seq:06d}"

# --- NUEVA FUNCIÓN AÑADIDA ---
def generar_numero_liquidacion(planta_codigo):
    """
    Genera un número de liquidación único y consecutivo.
    Formato: LQ-[CODIGO_PLANTA]-[AÑO]-[NUMERO_SECUENCIAL]
    Ejemplo: LQ-P01-2025-000001
    """
    from app import db
    current_year = datetime.now().year

    last_liq_str = db.session.query(db.func.max(Liquidacion.numero_liquidacion)).filter(
        Liquidacion.numero_liquidacion.like(f'LQ-{planta_codigo}-{current_year}-%')
    ).scalar()

    new_seq = 1
    if last_liq_str:
        last_seq = int(last_liq_str.split('-')[-1])
        new_seq = last_seq + 1
        
    return f"LQ-{planta_codigo}-{current_year}-{new_seq:06d}"

def generar_qr_code(data, filename, static_folder_path):
    """
    Genera un código QR y lo guarda en la carpeta de QRs.
    Retorna la ruta relativa para usar en plantillas HTML.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    qr_path = os.path.join(static_folder_path, 'qr_codes')
    os.makedirs(qr_path, exist_ok=True)
    
    img_path = os.path.join(qr_path, f"{filename}.png")
    img.save(img_path)
    
    return f"qr_codes/{filename}.png"