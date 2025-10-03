# init_data.py
from app import create_app, db

def init_database():
    app = create_app()
    
    with app.app_context():
        # Importar desde app.models.user
        from app.models.user import Role, Planta, User
        from flask_security import SQLAlchemyUserDatastore
        
        print("✅ Modelos importados desde app.models.user")
        
        # Crear roles usando el método estático
        Role.insert_roles()
        print("✅ Roles creados exitosamente!")
        
        # Crear plantas usando el método estático  
        Planta.insert_plantas()
        print("✅ Plantas creadas exitosamente!")
        
        # Crear usuario admin
        user_datastore = SQLAlchemyUserDatastore(db, User, Role)
        
        admin_user = User.query.filter_by(email='admin@sgpa.com').first()
        if not admin_user:
            user_datastore.create_user(
                email='admin@sgpa.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema',
                active=True
            )
            db.session.commit()
            
            admin_user = User.query.filter_by(email='admin@sgpa.com').first()
            admin_role = Role.query.filter_by(name='Admin').first()
            
            if admin_role:
                user_datastore.add_role_to_user(admin_user, admin_role)
                db.session.commit()
                print("✅ Usuario administrador creado: admin@sgpa.com / admin123")
            else:
                print("⚠️  Rol Admin no encontrado")
        else:
            print("✅ Usuario administrador ya existe")

if __name__ == '__main__':
    init_database()