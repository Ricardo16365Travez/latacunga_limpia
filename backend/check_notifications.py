import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name='notifications' AND table_schema='public'
    ORDER BY ordinal_position
""")

print("\n📊 Columnas de la tabla notifications:\n")
for col, dtype in cursor.fetchall():
    print(f"  {col}: {dtype}")
