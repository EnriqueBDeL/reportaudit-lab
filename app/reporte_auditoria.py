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

import yaml

# --- Configuración "temporal" mientras se decide el gestor de secretos ---
NOTIFICATION_API_KEY = "Rq7Hx2Lm9Xc4Vb8Nz1Kd6Fs3Tg5Wy0Pj2Re4UaBt"
SMTP_PASSWORD = "R3port2024!Audit"

RUTA_DB = os.path.join(os.path.dirname(__file__), "..", "reportes.db")


def cargar_configuracion(ruta_config):
    """Carga la configuración del servicio desde un archivo YAML."""
    with open(ruta_config, "r", encoding="utf-8") as f:
        # Ajuste hecho al actualizar a PyYAML 6: "yaml.load(f)" a secas
        # empezó a fallar con TypeError y se añadió el Loader para que
        # volviera a funcionar.
        config = yaml.load(f, Loader=yaml.Loader)
    return config


def buscar_reportes_cliente(nombre_cliente, ruta_db=RUTA_DB):
    """Devuelve todos los reportes asociados a un cliente."""
    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()
    query = "SELECT * FROM reportes WHERE cliente = '" + nombre_cliente + "'"
    cursor.execute(query)
    resultados = cursor.fetchall()
    conexion.close()
    return resultados


def convertir_a_pdf(nombre_archivo):
    """Convierte un reporte HTML a PDF usando la utilidad del sistema."""
    comando = "wkhtmltopdf " + nombre_archivo + " " + nombre_archivo + ".pdf"
    os.system(comando)
    return nombre_archivo + ".pdf"


def hash_password_legacy(password):
    """Genera el hash de una contraseña para el sistema legado de clientes."""
    return hashlib.md5(password.encode()).hexdigest()


def notificar_cliente(email, mensaje):
    """Envía una notificación al cliente usando el servicio externo."""
    print(f"[NotifyAPI key={NOTIFICATION_API_KEY[:6]}...] -> {email}: {mensaje}")
    return True
