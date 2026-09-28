## Issue relacionado

<!-- Closes #N  (el PR cerrará el Issue automáticamente al fusionarse) -->

## Qué cambia y por qué

<!-- Una o dos frases: el problema que existía y cómo lo resuelve este cambio -->

## Hallazgos que resuelve (si aplica)

| Herramienta que lo detectó | Regla / CVE | Archivo:línea | Clasificación (SAST / SCA / Secreto) | Severidad |
|---|---|---|---|---|
|  |  |  |  |  |

## Evidencia de verificación

<!-- Qué ejecutaste DESPUÉS del cambio para comprobar que funciona y que el hallazgo desapareció -->

## Decisiones justificadas (VEX / riesgo aceptado)

<!-- Si algún hallazgo NO se corrige, explica por qué no es explotable y enlaza el documento VEX -->

## Checklist del autor

- [ ] El título del PR sigue Conventional Commits (`tipo(ámbito): descripción`)
- [ ] Volví a ejecutar la herramienta que detectó cada hallazgo y ya no aparece (o quedó justificado)
- [ ] No añadí ningún secreto nuevo al repositorio
- [ ] `python app/servicio.py` sigue arrancando y respondiendo
- [ ] Los checks del pipeline están en verde
