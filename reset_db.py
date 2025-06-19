from app import db  # sesuaikan dengan nama app kamu
from sqlalchemy import text

with db.engine.connect() as conn:
    conn.execute(text("SET session_replication_role = replica;"))
    
    # Ambil semua tabel
    tables = db.metadata.sorted_tables
    for table in tables:
        conn.execute(text(f'TRUNCATE TABLE "{table.name}" CASCADE;'))
    
    conn.execute(text("SET session_replication_role = DEFAULT;"))
