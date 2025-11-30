import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("""
    SELECT table_schema, table_name 
    FROM information_schema.tables 
    WHERE table_schema NOT IN ('pg_catalog', 'information_schema', 'auth', 'storage', 'supabase_functions', 'extensions', 'graphql', 'graphql_public', 'pgsodium', 'pgsodium_masks', 'realtime', 'supabase_migrations', 'vault')
    ORDER BY table_schema, table_name
""")

print("\n📊 Tablas disponibles en la base de datos:\n")
tables = cursor.fetchall()
if tables:
    for schema, table in tables:
        print(f"  {schema}.{table}")
else:
    print("  ⚠️  No se encontraron tablas de usuario\n")
    
print(f"\n  Total: {len(tables)} tablas\n")
