"""
ReportAudit — lógica de negocio del servicio de reportes de auditoría.

Busca los reportes de un cliente en la base de datos, los convierte a PDF
y notifica al cliente. En producción desde hace 18 meses; nadie lo ha
revisado desde entonces.

Punto de partida del Laboratorio 1 de Calidad de Software: este módulo
contiene problemas reales de seguridad, sembrados a propósito, que el
estudiante debe encontrar (primero a mano y luego con herramientas) y
corregir. No uses este código como ejemplo de cómo hacer las cosas.
"""

import hashlib
import os
import re
import sqlite3
import subprocess
from pathlib import Path

import yaml

NOTIFICATION_API_KEY = os.getenv("NOTIFICATION_API_KEY", "")

RUTA_DB = os.path.join(os.path.dirname(__file__), "..", "reportes.db")


def cargar_configuracion(ruta_config):
    """Carga la configuración del servicio desde un archivo YAML."""
    with open(ruta_config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


def buscar_reportes_cliente(nombre_cliente, ruta_db=RUTA_DB):
    """Devuelve todos los reportes asociados a un cliente."""
    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()
    query = "SELECT * FROM reportes WHERE cliente = ?"
    cursor.execute(query, (nombre_cliente,))
    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def _validar_nombre_archivo(nombre_archivo):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+\.html", nombre_archivo):
        raise ValueError("Nombre de archivo no válido")


def convertir_a_pdf(nombre_archivo):
    """Convierte un reporte HTML a PDF usando la utilidad del sistema."""
    _validar_nombre_archivo(nombre_archivo)
    ruta_html = Path(nombre_archivo)
    contenido_html = ruta_html.read_bytes()
    resultado = subprocess.run(
        ["wkhtmltopdf", "-", "-"],
        input=contenido_html,
        capture_output=True,
        check=True,
    )
    ruta_pdf = ruta_html.with_suffix(".pdf")
    ruta_pdf.write_bytes(resultado.stdout)
    return str(ruta_pdf)


def hash_password_legacy(password):
    """Genera el hash de una contraseña para el sistema legado de clientes."""
    salt = os.urandom(16)
    hash_derivado = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600_000)
    return f"{salt.hex()}:{hash_derivado.hex()}"


def notificar_cliente(email, mensaje):
    """Envía una notificación al cliente usando el servicio externo."""
    _ = mensaje
    estado_api = "configurada" if NOTIFICATION_API_KEY else "sin_configurar"
    print(f"[NotifyAPI:{estado_api}] Notificación enviada a {email}")
    return True
