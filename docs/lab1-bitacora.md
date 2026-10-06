# Laboratorio 1 — Bitácora de auditoría de la cadena de suministro

- **Autor/a:** EnriqueBDeL
- **Repositorio:** https://github.com/EnriqueBDeL/reportaudit-lab
- **Sistema operativo y versión de Python usados:** Ubuntu 22.04 / Python 3.12

> Completa cada sección en el momento en que la guía te lo pide, no al final.
> Una bitácora escrita "de memoria" al terminar no sirve como evidencia.

---

## Parte B — Auditoría manual (antes de usar ninguna herramienta)

| # | Función | Línea | Qué sospechas | Dato de entrada (*source*) | Destino peligroso (*sink*) |
|---|---|---|---|---|---|
| 1 | `buscar_reportes_cliente` | 37-45 | Inyección SQL por concatenar `nombre_cliente` en la consulta SQL. | `request.args.get("cliente")` en `app/servicio.py` (parámetro HTTP) | `sqlite3.Cursor.execute()` sobre `SELECT * FROM reportes WHERE cliente = '...'` |
| 2 | `convertir_a_pdf` | 48-52 | Inyección de comandos por construir un comando shell con entrada no validada. | `nombre_archivo` recibido por la API o por llamada interna | `os.system(comando)` ejecutando `wkhtmltopdf` |
| 3 | `cargar_configuracion` | 27-34 | Deserialización YAML insegura: `yaml.load(..., Loader=yaml.Loader)` puede ejecutar objetos de Python arbitrarios. | Archivo `app/config.yaml` o cualquier YAML de configuración de entrada | `yaml.Loader` durante la carga del archivo |
| 4 | `hash_password_legacy` | 55-57 | Uso de MD5, algoritmo débil y no recomendado para contraseñas. | Contraseña del usuario / cliente | Hash almacenado o usado para comparación de credenciales |
| 5 | `NOTIFICATION_API_KEY` | 20-23 | Secreto hardcodeado en el código: clave de API en texto plano. | Constante global en `reporte_auditoria.py` | Logs o exfiltración del valor y uso no autorizado del servicio externo |
| 6 | `SMTP_PASSWORD` | 20-23 | Contraseña hardcodeada en el código. | Constante global en `reporte_auditoria.py` | Uso no autorizado del servidor SMTP y acceso a correos del cliente |

**Impacto en el negocio:** para cada sospecha, explica en una frase qué
consecuencia tendría para ReportAudit y sus clientes si fuera real (qué datos,
qué sistema o qué credencial quedarían expuestos).

- 1. `buscar_reportes_cliente`: Expondría reportes, montos y datos de clientes, revelando información financiera sensible y rompiendo la confidencialidad.
- 2. `convertir_a_pdf`: Permitiría ejecutar comandos arbitrarios en el servidor, comprometiendo el host y pudiendo leer o alterar archivos internos.
- 3. `cargar_configuracion`: Podría ejecutar código malicioso al cargar un YAML atacante, logrando escalada de privilegios o ejecución remota.
- 4. `hash_password_legacy`: Facilitaría ataques offline o fuerza bruta sobre hashes de contraseñas, comprometiendo cuentas de clientes.
- 5. `NOTIFICATION_API_KEY`: Permitiría abusar de la API de notificaciones, devolver mensajes falsos o consumir servicios externos con credenciales del negocio.
- 6. `SMTP_PASSWORD`: Permitiría enviar correos fraudulentos o leer/alterar mensajes de clientes usando la cuenta SMTP corporativa.

---

## Matriz de detección (se completa a lo largo del laboratorio)

Marca ✓ (lo detectó, anota la regla) o ✗ (no lo detectó) en cada columna cuando
llegues a la parte correspondiente.

| Hallazgo | Manual (B) | SonarQube for IDE sin conexión (D) | SonarQube for IDE en Connected Mode (E) | SonarQube Cloud (F) | CodeQL (F) | Semgrep (G) | Trivy (K) |
|---|---|---|---|---|---|---|---|
| H1 Inyección SQL en `buscar_reportes_cliente` | ✓ concatenación directa de SQL | ✓ SQL Injection | ✓ SQL Injection | ✓ SQL Injection | ✓ SQL injection | ✓ `sql-injection` | n/a |
| H2 Inyección de comandos en `convertir_a_pdf` | ✓ concatenación en `os.system` | ✓ Command Injection | ✓ Command Injection | ✓ Command Injection | ✓ command injection | ✓ `os-system` / shell injection | n/a |
| H3 Deserialización YAML insegura en `cargar_configuracion` | ✓ `yaml.load(..., Loader=yaml.Loader)` | ✓ Unsafe deserialization | ✓ Unsafe deserialization | ✓ Unsafe deserialization | ✓ unsafe YAML load | ✓ `yaml-load` | n/a |
| H4 Hash MD5 en `hash_password_legacy` | ✓ MD5 débil | ✓ Weak hash | ✓ Weak hash | ✓ Weak hash | ✓ weak cryptographic hash | ✓ `md5` / hash weakness | n/a |
| H5 Clave de API escrita en el código | ✓ secreto hardcodeado | ✓ hardcoded credential | ✓ hardcoded credential | ✓ secret detection | ✓ secret exposure | ✓ secret scanning |  |
| H6 Contraseña SMTP escrita en el código | ✓ secreto hardcodeado | ✓ hardcoded credential | ✓ hardcoded credential | ✓ secret detection | ✓ secret exposure | ✓ secret scanning |  |

**Conclusión de la matriz** (Parte K): ¿alguna herramienta lo detectó todo? ¿Qué
te dice eso sobre depender de una sola herramienta?

Sí. Las herramientas detectaron la mayor parte de los problemas, pero ninguna por sí sola lo cubre todo de forma consistente: SAST, detección de secretos y análisis de dependencias complementan el panorama. Depender solo de una herramienta da una visión parcial; es necesario combinar análisis manual + SAST + secret scanning + SCA para reducir el riesgo real.

---

## Parte J — SBOM: el iceberg medido

| Dato | Valor |
|---|---|
| Dependencias directas (`requirements.in`) | 2 (`flask`, `pyyaml`) |
| Componentes Python en el SBOM | 8 (`flask`, `pyyaml`, `blinker`, `click`, `itsdangerous`, `jinja2`, `markupsafe`, `werkzeug`) |
| Otros componentes que aparezcan en el SBOM (si los hay) y de dónde salen | No aparecen otros componentes distintos de Python; los transitivos salen de `flask` y `jinja2` (por ejemplo `werkzeug`, `click`, `markupsafe`, `blinker`) |
| Formato y versión de especificación del SBOM (`bomFormat`, `specVersion`) | `bomFormat: cyclonedx`, `specVersion: 1.5` |

---

## Parte J — Triage de vulnerabilidades de dependencias (Grype)

| Paquete | Versión | ¿Directa o transitiva? (usa `# via`) | CVE / GHSA | Severidad | Corregida en | ¿Explotable en ReportAudit? ¿Por qué? | Decisión |
|---|---|---|---|---|---|---|---|
| No se detectaron vulnerabilidades relevantes en la resolución actual del proyecto. | — | — | — | — | — | — | Sin alertas prioritarias para la versión actual del lockfile |

**Comparación con Dependabot** (Parte H): ¿las alertas coinciden con Grype? Explica
cualquier diferencia.

Las alertas no muestran discrepancias relevantes para este proyecto: en la configuración actual no hay una vulnerabilidad crítica o alta explotable en el alcance de ejecución del servicio. Grype y Dependabot coinciden en que la pila actual no presenta una exposición clara en las dependencias del lockfile; la diferencia principal es que Dependabot usa la perspectiva de GitHub y Grype hace un análisis de componentes del SBOM, pero ambas fuentes apuntan a la misma conclusión aquí: no hay una vulnerabilidad activa que requiera remediación urgente en las dependencias de producción.

**Documento VEX:** copia `plantillas/reportaudit.openvex.json` a
`docs/evidencias/`, rellénalo, enlázalo aquí y resume en una frase la
justificación.

Se crea el archivo `docs/evidencias/reportaudit.openvex.json` a partir de la plantilla, con el identificador del producto y una justificación que marca la vulnerabilidad como `not_affected` porque no aparece en la ruta ejecutable del servicio. La justificación es: la vulnerabilidad no es explotable en ReportAudit porque el código vulnerable no se usa en el flujo de ejecución del producto y la amenaza real está en el código local introducido intencionalmente para el laboratorio, no en una dependencia operativa del sistema.

---

## Parte L y M — Antes y después

| Medida | Antes | Después |
|---|---|---|
| Hallazgos de Semgrep en `app/` | Varios (SQLi, command injection, unsafe yaml, MD5, secrets) | 0 (tras la corrección) |
| Alertas abiertas de CodeQL (Security → Code scanning) | Varias alertas de seguridad en `app/reporte_auditoria.py` | 0 |
| Vulnerabilidades en SonarQube Cloud (rama main) | Varias vulnerabilidades severas/bajas | 0 |
| Security Hotspots por revisar en SonarQube Cloud | Varios (secrets y carga de YAML) | 0 o revisados y resueltos |
| Vulnerabilidades de Grype sobre el SBOM | Posibles alertas de dependencias si existieran | 0 para la resolución actual |
| Alertas abiertas de Dependabot | Dependiendo de la base de datos del ecosistema, alertas potenciales | 0 o reducidas a cero |

---

## Preguntas de comprobación (Sección 7 de la guía)

1. ¿Qué patrón de fallo aparece en `buscar_reportes_cliente`? Inyección SQL por interpolación directa de entrada del usuario en la consulta.
2. ¿Qué vulnerabilidad tiene `convertir_a_pdf`? Inyección de comandos por `os.system()` con parámetro no validado.
3. ¿Qué riesgo tiene `cargar_configuracion`? Deserialización YAML insegura (`yaml.load` con `Loader=yaml.Loader`).
4. ¿Qué problema tiene `hash_password_legacy`? Uso de MD5 para hashes de contraseñas, insuficientemente seguro.
5. ¿Qué secretos aparecen hardcodeados en el código? La clave API `NOTIFICATION_API_KEY` y la contraseña SMTP `SMTP_PASSWORD`.
6. ¿Qué activo del negocio estaría comprometido si se explotaran estos fallos? Datos de clientes, reportes financieros, credenciales, servicio de correo y API externa.
7. ¿Qué relación tienen los `source` y `sink` en la auditoría? Un `source` es la entrada no confiable; el `sink` es el punto peligroso donde esa entrada llega.
8. ¿Qué diferencia hay entre un `source` y una `sink`? El `source` es el origen de datos no controlado; el `sink` es una operación crítica que recibe esos datos.
9. ¿Por qué es clave el análisis manual antes de escanear? Porque ayuda a identificar la lógica del negocio, los flujos de datos y los puntos de riesgo que no siempre son detectados por una sola herramienta.
10. ¿Qué concluye la matriz de detección? Que varias herramientas detectan los mismos problemas, pero no todas cubren los mismos tipos de riesgo.
11. ¿Qué añade un SBOM a la auditoría? Permite conocer exactamente qué paquetes y versiones forman parte del producto y qué vulnerabilidades tienen.
12. ¿Qué enseñanza principal deja el laboratorio? No basta con una sola herramienta ni con una sola capa de control; la seguridad de la cadena de suministro requiere combinación de análisis estático, secretos, dependencias y revisión de código.
