"""
ReportAudit — servicio HTTP.

Expone la lógica de reporte_auditoria.py como una pequeña API web interna.
Se ejecuta en local con:

    python app/servicio.py

y queda escuchando en http://127.0.0.1:8080
"""

from pathlib import Path

from flask import Flask, jsonify, request

from reporte_auditoria import (
    buscar_reportes_cliente,
    cargar_configuracion,
    convertir_a_pdf,
)

RUTA_CONFIG = Path(__file__).with_name("config.yaml")
config = cargar_configuracion(RUTA_CONFIG)

app = Flask(__name__)


@app.get("/")
def inicio():
    """Describe el servicio y sus endpoints."""
    return jsonify(
        servicio=config["servicio"]["nombre"],
        entorno=config["servicio"]["entorno"],
        endpoints=["/reportes?cliente=<nombre>", "/convertir?archivo=<archivo.html>"],
    )


@app.get("/reportes")
def reportes():
    """Devuelve los reportes de un cliente en formato JSON."""
    cliente = request.args.get("cliente", "")
    filas = buscar_reportes_cliente(cliente)
    return jsonify(
        cliente_solicitado=cliente,
        total_registros=len(filas),
        reportes=[{"id": f[0], "cliente": f[1], "monto": f[2]} for f in filas],
    )


@app.get("/convertir")
def convertir():
    """Convierte a PDF un reporte HTML ya generado en el servidor."""
    archivo = request.args.get("archivo", "")
    try:
        salida = convertir_a_pdf(archivo)
    except ValueError:
        return jsonify(error="Nombre de archivo no válido"), 400
    return jsonify(archivo_pdf=salida)


if __name__ == "__main__":
    # debug=False: el depurador interactivo de Werkzeug NUNCA debe
    # activarse en un servicio accesible por otras personas.
    app.run(host="127.0.0.1", port=config["servicio"]["puerto"], debug=False)
