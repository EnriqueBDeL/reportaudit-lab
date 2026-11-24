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
import sqlite3
import subprocess
from pathlib import Path

import yaml

NOTIFICATION_API_KEY = os.environ.get("REPORTAUDIT_NOTIFICATION_API_KEY", "")
SMTP_PASSWORD = os.environ.get("REPORTAUDIT_SMTP_PASSWORD", "")

RUTA_DB = os.path.join(os.path.dirname(__file__), "..", "reportes.db")
CARACTERES_INICIALES_HTML = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"
CARACTERES_VALIDOS_HTML = CARACTERES_INICIALES_HTML + ".-"


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


def convertir_a_pdf(nombre_archivo):
    """Convierte un reporte HTML a PDF usando la utilidad del sistema."""
    if (
        not isinstance(nombre_archivo, str)
        or len(nombre_archivo) > 255
        or Path(nombre_archivo).name != nombre_archivo
        or not nombre_archivo.endswith(".html")
        or not nombre_archivo[:-5]
        or nombre_archivo[0] not in CARACTERES_INICIALES_HTML
        or any(
            caracter not in CARACTERES_VALIDOS_HTML
            for caracter in nombre_archivo[1:-5]
        )
    ):
        raise ValueError("Nombre de archivo no válido")

    salida = nombre_archivo + ".pdf"
    try:
        subprocess.run(["wkhtmltopdf", nombre_archivo, salida], check=True)
    except FileNotFoundError as exc:
        print("Aviso: wkhtmltopdf no está instalado; no se generó el PDF.")
        raise RuntimeError("No se pudo generar el PDF porque falta wkhtmltopdf.") from exc
    return salida


def hash_password_legacy(password):
    """Genera un hash PBKDF2 con sal aleatoria para una contraseña."""
    sal = os.urandom(16)
    derivado = hashlib.pbkdf2_hmac("sha256", password.encode(), sal, 600_000)
    return sal.hex() + ":" + derivado.hex()


def notificar_cliente(email, mensaje):
    """Envía una notificación al cliente usando el servicio externo."""
    print(f"[NotifyAPI configured={bool(NOTIFICATION_API_KEY)}] -> {email}: {mensaje}")
    return True
