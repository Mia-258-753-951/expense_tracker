
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / 'data/expenses.db'
SQL_PATH = Path(__file__).resolve().parents[2] / 'migrations/001_init.sql'
SCHEMA_VERSION = 1

def init_db(path: Path=DB_PATH) -> None:    
    if path.exists():
        conexion = sqlite3.connect(str(path))
        try:        
            version= conexion.execute(
                '''SELECT * FROM schema_version'''
            ).fetchone()
            
            if version[0] != SCHEMA_VERSION:
                raise ValueError(
                            f"schema_version '{version[0]}' not supported. "
                            f"Supported version: '{SCHEMA_VERSION}'."
                            )
        finally:
            conexion.close()
    else:
        path.parent.mkdir(exist_ok=True, parents=True)          
        with SQL_PATH.open('r', encoding='utf-8') as f:
            schema_sql = f.read()
            
        conexion = sqlite3.connect(str(path))    
        try:
            with conexion:
                # Conectamos y ejecutamos todo el script de golpe
                conexion.executescript(schema_sql)
        finally:
            conexion.close()
        
        
        
if __name__ == '__main__':
    init_db()
        


