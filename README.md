# ReportAudit — repositorio base de Calidad de Software

Servicio interno (Python + Flask) que consulta reportes de auditoría de clientes,
los convierte a PDF y notifica al cliente. Es el repositorio de trabajo de:

- **Laboratorio 1** — Cadena de suministro segura: SAST, SCA y SBOM desde cero.
- **Laboratorio 2** — Revisión estructural: SOLID, patrones de diseño y métricas de flujo.

> Este código contiene problemas de seguridad **sembrados a propósito** con fines
> docentes. No lo despliegues en ningún servidor accesible por otras personas.

## Puesta en marcha (resumen — el detalle está en la guía del laboratorio)

```bash
python -m venv venv
source venv/bin/activate          # Windows (Git Bash): source venv/Scripts/activate
python -m pip install -r requirements.txt
python scripts/inicializar_db.py
python app/servicio.py            # http://127.0.0.1:8080
```

## Estructura

| Ruta | Contenido |
|---|---|
| `app/` | Código del servicio (`servicio.py`) y su lógica (`reporte_auditoria.py`) |
| `scripts/` | Utilidades: crear la base de datos local, instalar herramientas verificadas |
| `plantillas/` | Archivos de configuración que se activan, uno a uno, durante el Laboratorio 1 |
| `docs/` | Bitácora del laboratorio y evidencias (SBOM, informes de escaneo, VEX) |
| `requirements.in` | Dependencias **directas** (lo que el equipo decidió usar) |
| `requirements.txt` | *Lockfile*: TODAS las dependencias, directas y transitivas, con versión exacta |

Autor/a: ESCRIBE_AQUÍ_TU_NOMBRE_Y_APELLIDOS
Profesor: Dr. Richard Avilés López
