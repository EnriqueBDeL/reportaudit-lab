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

import yaml

NOTIFICATION_API_KEY = os.getenv("NOTIFICATION_API_KEY", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

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
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", nombre_archivo):
        raise ValueError("Nombre de archivo no válido")


def convertir_a_pdf(nombre_archivo):
    """Convierte un reporte HTML a PDF usando la utilidad del sistema."""
    _validar_nombre_archivo(nombre_archivo)
    comando = ["wkhtmltopdf", nombre_archivo, f"{nombre_archivo}.pdf"]
    subprocess.run(comando, check=True)
    return nombre_archivo + ".pdf"


def hash_password_legacy(password):
    """Genera el hash de una contraseña para el sistema legado de clientes."""
    return hashlib.sha256(password.encode()).hexdigest()


def notificar_cliente(email, mensaje):
    """Envía una notificación al cliente usando el servicio externo."""
    print(f"[NotifyAPI key={NOTIFICATION_API_KEY[:6]}...] -> {email}: {mensaje}")
    return True
