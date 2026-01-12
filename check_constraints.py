"""Script para verificar constraints de las tablas"""
import os
from sqlalchemy import create_engine, text, inspect

# Conectar a Neon
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_XBw8xVBZJRAm@ep-gentle-pond-a9dcmrdsv-pooler.us-east-1.aws.neon.tech/neondb")
engine = create_engine(DATABASE_URL)

def check_table_constraints(table_name):
    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT conname, pg_get_constraintdef(oid) 
            FROM pg_constraint 
            WHERE conrelid = (
                SELECT oid FROM pg_class 
                WHERE relname = '{table_name}' 
                AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
            ) 
            AND contype = 'c'
        """))
        
        constraints = list(result)
        if constraints:
            print(f"\n{'='*60}")
            print(f"CHECK CONSTRAINTS para tabla: {table_name}")
            print(f"{'='*60}")
            for row in constraints:
                print(f"  • {row[0]}: {row[1]}")
        else:
            print(f"\n❌ No se encontraron CHECK constraints para: {table_name}")

def check_columns(table_name):
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    print(f"\n{'='*60}")
    print(f"COLUMNAS de tabla: {table_name}")
    print(f"{'='*60}")
    for col in columns:
        nullable = "NULL" if col['nullable'] else "NOT NULL"
        print(f"  • {col['name']:25} {str(col['type']):20} {nullable}")

# Verificar las tablas con errores
tables = ['conductores', 'reports', 'incidencias']
for table in tables:
    check_table_constraints(table)
    check_columns(table)

print(f"\n{'='*60}\n")
