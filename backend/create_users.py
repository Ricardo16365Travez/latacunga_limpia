"""
Script para crear usuarios de prueba en el sistema
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_users():
    """Crear usuarios de prueba"""
    
    # Crear o actualizar superusuario
    admin_email = 'admin@latacunga.gob.ec'
    if User.objects.filter(email=admin_email).exists():
        admin = User.objects.get(email=admin_email)
        print(f"✓ Admin ya existe: {admin_email}")
    else:
        admin = User.objects.create_superuser(
            email=admin_email,
            password='admin123',
            first_name='Administrador',
            last_name='Sistema'
        )
        print(f"✓ Superusuario creado: {admin_email}")
    
    # Asegurar que tiene contraseña y permisos
    admin.set_password('admin123')
    admin.is_staff = True
    admin.is_superuser = True
    admin.is_active = True
    admin.role = 'super_admin'
    admin.status = 'ACTIVE'
    admin.display_name = 'Administrador del Sistema'
    admin.save()
    
    print(f"\n{'='*60}")
    print(f"CREDENCIALES DE ACCESO:")
    print(f"{'='*60}")
    print(f"Email:    {admin_email}")
    print(f"Password: admin123")
    print(f"Rol:      Super Administrador")
    print(f"{'='*60}\n")
    
    # Crear usuario administrador regular
    admin2_email = 'administrador@latacunga.gob.ec'
    if not User.objects.filter(email=admin2_email).exists():
        admin2 = User.objects.create_user(
            email=admin2_email,
            password='admin123',
            first_name='Admin',
            last_name='Latacunga'
        )
        admin2.is_staff = True
        admin2.role = 'admin'
        admin2.display_name = 'Administrador'
        admin2.save()
        print(f"✓ Administrador creado: {admin2_email} / admin123")
    
    # Crear usuario operador
    operador_email = 'operador@latacunga.gob.ec'
    if not User.objects.filter(email=operador_email).exists():
        operador = User.objects.create_user(
            email=operador_email,
            password='operador123',
            first_name='Operador',
            last_name='Campo'
        )
        operador.role = 'operador'
        operador.display_name = 'Operador de Campo'
        operador.save()
        print(f"✓ Operador creado: {operador_email} / operador123")
    
    # Crear usuario trabajador
    trabajador_email = 'trabajador@latacunga.gob.ec'
    if not User.objects.filter(email=trabajador_email).exists():
        trabajador = User.objects.create_user(
            email=trabajador_email,
            password='trabajador123',
            first_name='Trabajador',
            last_name='Recolección'
        )
        trabajador.role = 'trabajador'
        trabajador.display_name = 'Trabajador de Recolección'
        trabajador.save()
        print(f"✓ Trabajador creado: {trabajador_email} / trabajador123")
    
    # Crear usuario normal
    usuario_email = 'usuario@test.com'
    if not User.objects.filter(email=usuario_email).exists():
        usuario = User.objects.create_user(
            email=usuario_email,
            password='usuario123',
            first_name='Usuario',
            last_name='Prueba'
        )
        usuario.role = 'user'
        usuario.display_name = 'Usuario de Prueba'
        usuario.save()
        print(f"✓ Usuario creado: {usuario_email} / usuario123")
    
    print(f"\n{'='*60}")
    print(f"RESUMEN DE USUARIOS CREADOS:")
    print(f"{'='*60}")
    print(f"Total usuarios: {User.objects.count()}")
    print(f"Superusuarios:  {User.objects.filter(is_superuser=True).count()}")
    print(f"Staff:          {User.objects.filter(is_staff=True).count()}")
    print(f"Activos:        {User.objects.filter(is_active=True).count()}")
    print(f"{'='*60}\n")
    
    print(f"\n{'='*60}")
    print(f"TODOS LOS USUARIOS DEL SISTEMA:")
    print(f"{'='*60}")
    for user in User.objects.all().order_by('-is_superuser', '-is_staff', 'email'):
        print(f"- {user.email:35} | Rol: {user.role:15} | Staff: {user.is_staff} | Super: {user.is_superuser}")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    create_users()
