from app import create_app, db

app = create_app()

with app.app_context():
    print("🛠️ APLICANDO CORRECCIONES A LA BASE DE DATOS...")
    
    try:
        # 1. Agregar columna observaciones a proceso_desmotado si no existe
        print("\n1. VERIFICANDO COLUMNA 'observaciones' EN proceso_desmotado...")
        
        # Primero verificar si ya existe
        with db.engine.connect() as conn:
            result = conn.execute(db.text("PRAGMA table_info(proceso_desmotado)"))
            columns = [row[1] for row in result]
        
        if 'observaciones' in columns:
            print("   ✅ La columna 'observaciones' ya existe")
        else:
            print("   ➕ Agregando columna 'observaciones'...")
            with db.engine.begin() as conn:  # begin() maneja automáticamente commit
                conn.execute(db.text("ALTER TABLE proceso_desmotado ADD COLUMN observaciones TEXT"))
            print("   ✅ Columna 'observaciones' agregada exitosamente")
        
        # 2. Crear tabla liquidacion si no existe
        print("\n2. VERIFICANDO TABLA 'liquidacion'...")
        
        with db.engine.connect() as conn:
            result = conn.execute(db.text("SELECT name FROM sqlite_master WHERE type='table' AND name='liquidacion'"))
            if result.fetchone():
                print("   ✅ La tabla 'liquidacion' ya existe")
            else:
                print("   ➕ Creando tabla 'liquidacion'...")
                create_liquidacion_sql = """
                CREATE TABLE liquidacion (
                    id INTEGER PRIMARY KEY,
                    carga_id INTEGER NOT NULL UNIQUE,
                    numero_liquidacion VARCHAR(20) NOT NULL UNIQUE,
                    fecha_liquidacion DATETIME,
                    precio_kilo_bruto FLOAT NOT NULL,
                    total_bruto FLOAT NOT NULL,
                    anticipo FLOAT DEFAULT 0.0,
                    retenciones FLOAT DEFAULT 0.0,
                    otras_deducciones FLOAT DEFAULT 0.0,
                    total_a_pagar FLOAT NOT NULL,
                    observaciones TEXT,
                    usuario_id INTEGER NOT NULL,
                    FOREIGN KEY (carga_id) REFERENCES carga (id),
                    FOREIGN KEY (usuario_id) REFERENCES user (id)
                )
                """
                with db.engine.begin() as conn:
                    conn.execute(db.text(create_liquidacion_sql))
                print("   ✅ Tabla 'liquidacion' creada exitosamente")
        
        print("\n🎉 ¡BASE DE DATOS ACTUALIZADA CORRECTAMENTE!")
        print("🔍 Ejecuta 'python check_db.py' para verificar los cambios.")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")