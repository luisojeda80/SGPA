from app import create_app, db

app = create_app()

with app.app_context():
    print("=== VERIFICACIÓN DE LA BASE DE DATOS ===")
    
    # Verificar todas las tablas existentes
    print("\n📋 TODAS LAS TABLAS EN LA BD:")
    with db.engine.connect() as conn:
        result = conn.execute(db.text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
        tables = [row[0] for row in result]
        for table in tables:
            print(f"  - {table}")
    
    # Verificar específicamente proceso_desmotado
    print(f"\n🔍 DETALLES de 'proceso_desmotado':")
    try:
        with db.engine.connect() as conn:
            result = conn.execute(db.text("PRAGMA table_info(proceso_desmotado)"))
            columns = []
            print("  Columnas:")
            for row in result:
                columns.append(row[1])
                print(f"    - {row[1]} ({row[2]})")
            
            # Verificar si tiene la columna observaciones
            if 'observaciones' in columns:
                print("  ✅ La columna 'observaciones' SÍ existe")
            else:
                print("  ❌ La columna 'observaciones' NO existe")
                
    except Exception as e:
        print(f"  Error al verificar proceso_desmotado: {e}")
    
    # Verificar si existe liquidacion
    print(f"\n🔍 VERIFICANDO 'liquidacion':")
    try:
        with db.engine.connect() as conn:
            result = conn.execute(db.text("SELECT name FROM sqlite_master WHERE type='table' AND name='liquidacion'"))
            if result.fetchone():
                print("  ✅ La tabla 'liquidacion' EXISTE")
                # Mostrar sus columnas
                result = conn.execute(db.text("PRAGMA table_info(liquidacion)"))
                print("  Columnas:")
                for row in result:
                    print(f"    - {row[1]} ({row[2]})")
            else:
                print("  ❌ La tabla 'liquidacion' NO existe")
    except Exception as e:
        print(f"  Error al verificar liquidacion: {e}")