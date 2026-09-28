"""
Crea (o recrea) la base de datos local de ReportAudit con datos de ejemplo.

Uso, desde la raíz del repositorio:

    python scripts/inicializar_db.py

La base de datos (reportes.db) es un dato local: está en .gitignore y
nunca se sube al repositorio.
"""

import sqlite3
from pathlib import Path

RUTA_DB = Path(__file__).resolve().parent.parent / "reportes.db"

DATOS_DE_EJEMPLO = [
    ("acme_corp", 1500.0),
    ("acme_corp", 2300.0),
    ("globex", 900.0),
    ("initech", 4100.0),
    ("o'brien_ltd", 700.0),
]


def main():
    if RUTA_DB.exists():
        RUTA_DB.unlink()
    with sqlite3.connect(RUTA_DB) as conexion:
        conexion.execute(
            "CREATE TABLE reportes ("
            " id INTEGER PRIMARY KEY,"
            " cliente TEXT NOT NULL,"
            " monto REAL NOT NULL)"
        )
        conexion.executemany(
            "INSERT INTO reportes (cliente, monto) VALUES (?, ?)", DATOS_DE_EJEMPLO
        )
    conexion.close()
    print(f"Base de datos creada en {RUTA_DB} con {len(DATOS_DE_EJEMPLO)} reportes "
          f"de {len({c for c, _ in DATOS_DE_EJEMPLO})} clientes.")


if __name__ == "__main__":
    main()
