from app.database import engine
from sqlalchemy import text

tables = ['reports','incidencias','users','conductores']
with engine.connect() as conn:
    for t in tables:
        res = conn.execute(text(f"select count(*) from {t}"))
        print(f"{t}: {res.scalar()}")
