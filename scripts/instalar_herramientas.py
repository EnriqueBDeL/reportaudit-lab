"""
Instala Syft, Grype y Trivy en la carpeta tools/ del repositorio,
VERIFICANDO la integridad de cada descarga antes de usarla.

Uso, desde la raíz del repositorio (con cualquier Python 3.10+):

    python scripts/instalar_herramientas.py            # instala las tres
    python scripts/instalar_herramientas.py syft       # instala solo una

Qué hace, paso a paso, para cada herramienta:
  1. Descarga el archivo publicado para TU sistema operativo y arquitectura,
     en la versión EXACTA fijada abajo (nunca "la última").
  2. Descarga el archivo de sumas de verificación (checksums.txt) de esa
     misma versión.
  3. Calcula el SHA-256 del archivo descargado y lo compara con el publicado.
     Si no coinciden, se detiene y NO instala nada.
  4. Extrae únicamente el ejecutable dentro de tools/ (carpeta ignorada por Git).

Solo usa la biblioteca estándar de Python: no necesita instalar nada antes.
"""

import hashlib
import platform
import stat
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path

# Versiones fijadas (pinning). Cambiarlas es una decisión consciente del
# equipo, revisada en un Pull Request, no algo que ocurre solo.
VERSIONES = {
    "syft": "1.52.0",
    "grype": "0.119.0",
    "trivy": "0.74.0",
}

REPOSITORIOS = {
    "syft": "anchore/syft",
    "grype": "anchore/grype",
    "trivy": "aquasecurity/trivy",
}

CARPETA_TOOLS = Path(__file__).resolve().parent.parent / "tools"


def detectar_plataforma():
    """Devuelve (sistema, arquitectura) normalizados: ('linux'|'darwin'|'windows', 'amd64'|'arm64')."""
    sistema = platform.system().lower()
    maquina = platform.machine().lower()
    if sistema not in ("linux", "darwin", "windows"):
        raise SystemExit(f"Sistema operativo no soportado por este script: {sistema}")
    if maquina in ("x86_64", "amd64"):
        arquitectura = "amd64"
    elif maquina in ("arm64", "aarch64"):
        arquitectura = "arm64"
    else:
        raise SystemExit(f"Arquitectura no soportada por este script: {maquina}")
    return sistema, arquitectura


def nombre_del_archivo(herramienta, version, sistema, arquitectura):
    """Construye el nombre exacto del archivo publicado en GitHub Releases."""
    extension = "zip" if sistema == "windows" else "tar.gz"
    if herramienta in ("syft", "grype"):
        if herramienta == "grype" and sistema == "windows" and arquitectura == "arm64":
            raise SystemExit("Grype no publica binario para Windows ARM64: usa WSL2 o GitHub Codespaces.")
        return f"{herramienta}_{version}_{sistema}_{arquitectura}.{extension}"
    # Trivy usa otra convención de nombres
    so_trivy = {"linux": "Linux", "darwin": "macOS", "windows": "windows"}[sistema]
    arq_trivy = {"amd64": "64bit", "arm64": "ARM64"}[arquitectura]
    if sistema == "windows" and arquitectura == "arm64":
        raise SystemExit("Trivy no publica binario para Windows ARM64: usa WSL2 o GitHub Codespaces.")
    return f"trivy_{version}_{so_trivy}-{arq_trivy}.{extension}"


def descargar(url, destino):
    """Descarga una URL a un archivo local."""
    print(f"   descargando {url}")
    with urllib.request.urlopen(url, timeout=120) as respuesta, open(destino, "wb") as salida:
        while True:
            bloque = respuesta.read(1024 * 1024)
            if not bloque:
                break
            salida.write(bloque)


def sha256_de(ruta):
    """Calcula el SHA-256 de un archivo leyéndolo por bloques."""
    calculo = hashlib.sha256()
    with open(ruta, "rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            calculo.update(bloque)
    return calculo.hexdigest()


def sha256_publicado(ruta_checksums, nombre_archivo):
    """Busca en checksums.txt la línea '<sha256>  <nombre_archivo>' y devuelve el hash."""
    for linea in Path(ruta_checksums).read_text(encoding="utf-8").splitlines():
        partes = linea.split()
        if len(partes) == 2 and partes[1].lstrip("*") == nombre_archivo:
            return partes[0].lower()
    raise SystemExit(f"   ERROR: {nombre_archivo} no aparece en el archivo de checksums publicado.")


def extraer_ejecutable(archivo, herramienta, sistema):
    """Extrae SOLO el ejecutable de la herramienta dentro de tools/."""
    nombre_binario = herramienta + (".exe" if sistema == "windows" else "")
    destino = CARPETA_TOOLS / nombre_binario
    if str(archivo).endswith(".zip"):
        with zipfile.ZipFile(archivo) as zip_:
            miembro = next((m for m in zip_.namelist() if Path(m).name == nombre_binario), None)
            if miembro is None:
                raise SystemExit(f"   ERROR: {nombre_binario} no está dentro de {archivo}")
            destino.write_bytes(zip_.read(miembro))
    else:
        with tarfile.open(archivo, "r:gz") as tar:
            miembro = next((m for m in tar.getmembers() if m.isfile() and Path(m.name).name == nombre_binario), None)
            if miembro is None:
                raise SystemExit(f"   ERROR: {nombre_binario} no está dentro de {archivo}")
            # Se lee el contenido del miembro y se escribe con un nombre
            # elegido por nosotros: nunca se confía en las rutas internas
            # del archivo comprimido (evita ataques de "path traversal").
            destino.write_bytes(tar.extractfile(miembro).read())
    destino.chmod(destino.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return destino


def instalar(herramienta):
    version = VERSIONES[herramienta]
    sistema, arquitectura = detectar_plataforma()
    archivo = nombre_del_archivo(herramienta, version, sistema, arquitectura)
    base = f"https://github.com/{REPOSITORIOS[herramienta]}/releases/download/v{version}"
    print(f"\n== {herramienta} {version} ({sistema}/{arquitectura})")

    with tempfile.TemporaryDirectory() as temporal:
        ruta_archivo = Path(temporal) / archivo
        ruta_checksums = Path(temporal) / "checksums.txt"
        descargar(f"{base}/{archivo}", ruta_archivo)
        descargar(f"{base}/{herramienta}_{version}_checksums.txt", ruta_checksums)

        esperado = sha256_publicado(ruta_checksums, archivo)
        obtenido = sha256_de(ruta_archivo)
        print(f"   SHA-256 publicado: {esperado}")
        print(f"   SHA-256 calculado: {obtenido}")
        if esperado != obtenido:
            raise SystemExit("   ERROR: las sumas NO coinciden. Descarga corrupta o manipulada: no se instala nada.")
        print("   OK: integridad verificada")

        CARPETA_TOOLS.mkdir(exist_ok=True)
        ejecutable = extraer_ejecutable(ruta_archivo, herramienta, sistema)

    resultado = subprocess.run([str(ejecutable), "--version"], capture_output=True, text=True, check=False)
    primera_linea = (resultado.stdout or resultado.stderr).strip().splitlines()[:1]
    print(f"   instalado en {ejecutable.relative_to(CARPETA_TOOLS.parent)} -> {' '.join(primera_linea)}")


def main(argumentos):
    pedidas = argumentos or list(VERSIONES)
    desconocidas = [h for h in pedidas if h not in VERSIONES]
    if desconocidas:
        raise SystemExit(f"Herramienta desconocida: {', '.join(desconocidas)}. Opciones: {', '.join(VERSIONES)}")
    for herramienta in pedidas:
        instalar(herramienta)
    print("\nListo. Ejecuta las herramientas desde la raíz del repositorio, por ejemplo: ./tools/syft --version")


if __name__ == "__main__":
    main(sys.argv[1:])
