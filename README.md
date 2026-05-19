# INVIMA Hemato-Oncologia

**Herramienta local en Python para consultar y consolidar informacion regulatoria y clinica de medicamentos hemato-oncologicos en Colombia.**

**Martin Munive**<br>
Medico General<br>
Analista y programador de software

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-local-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Licencia](https://img.shields.io/badge/licencia-MIT-16A34A)](LICENSE)
[![Estado](https://img.shields.io/badge/estado-prototipo%20local-f59e0b)](#estado-del-proyecto)

> Este proyecto ayuda a revisar, organizar y presentar informacion de medicamentos oncologicos a partir de fuentes como INVIMA, UNIRS, POS Populi y un perfil manual curado. Su objetivo es reducir friccion operativa sin reemplazar la verificacion oficial, el juicio medico ni la revision regulatoria.

## Que es

`INVIMA-HematoOncologia` es un prototipo local para construir una ficha consolidada por medicamento. El sistema integra:

- registros sanitarios INVIMA por producto o presentacion;
- indicaciones INVIMA cuando estan disponibles en el detalle del registro;
- indicaciones complementarias UNIRS;
- cobertura o financiacion POS Populi / UPC;
- perfil manual oncologico curado: mecanismo, clase, efectos adversos, extravasacion, manejo e indicaciones resumidas;
- perfil clinico curado por medicamento cuando exista inmersion cientifica validada;
- trazabilidad de fuente para separar informacion regulatoria, complementaria y tecnica.

La unidad principal no es solo el principio activo. Para decisiones regulatorias importan tambien expediente, producto, presentacion, registro sanitario, estado del registro e indicacion textual.

## Para que sirve

El proyecto esta pensado para escenarios de hemato-oncologia donde se necesita responder rapidamente preguntas como:

- si un medicamento tiene registros INVIMA vigentes;
- para que enfermedades o escenarios aparece indicado segun INVIMA;
- si el principio activo aparece financiado con recursos UPC en POS Populi;
- que indicaciones complementarias aparecen en UNIRS;
- que tipo de medicamento es y cual es su mecanismo de accion;
- que eventos adversos, extravasacion, hipersensibilidad, anafilaxia o toxicidad deben revisarse;
- que fuente respalda cada afirmacion.

## Limites clinicos y regulatorios

Este repositorio no sustituye:

- la consulta oficial en INVIMA;
- la revision normativa vigente;
- el criterio medico;
- la validacion institucional para autorizacion de medicamentos;
- la revision farmaceutica, oncologica o administrativa de cada caso.

Una indicacion solo debe presentarse como **indicacion INVIMA** si proviene de una fuente INVIMA real. La literatura cientifica o el perfil manual pueden complementar mecanismo, seguridad o manejo, pero no convierten una indicacion en autorizacion regulatoria.

## Estado del proyecto

Estado actual: **prototipo local con CLI, API FastAPI e interfaz React/Vite**.

Implementado:

- parsers para resultados y detalles INVIMA guardados como HTML;
- parser de UNIRS desde XLSX;
- parser de POS Populi desde HTML guardado;
- parser de documento manual oncologico;
- base local SQLite;
- comandos de importacion, consulta y reporte;
- comando de cobertura para detectar medicamentos pendientes de detalle INVIMA;
- importacion por carpeta de resultados INVIMA guardados despues del CAPTCHA manual;
- API local FastAPI;
- frontend React/Vite con resumen regulatorio, UNIRS integrado y seguridad clinica curada para PACLITAXEL;
- pruebas unitarias iniciales;
- reporte consolidado funcional para `PACLITAXEL` en el entorno local de desarrollo.

Pendiente:

- importador de HAR o `Copy as cURL` para flujos post-CAPTCHA;
- trazabilidad ampliada de fuente primaria para indicaciones INVIMA;
- procesamiento progresivo de mas medicamentos.

## Instalacion local

Requisitos:

- Python 3.11 o superior.
- PowerShell, Windows Terminal o una terminal compatible.

Clonar el repositorio:

```powershell
git clone https://github.com/Martin-Munive/INVIMA-HematoOncologia.git
cd INVIMA-HematoOncologia
```

Instalar en modo editable:

```powershell
python -m venv .INVIMA
.\.INVIMA\Scripts\python.exe -m pip install -e .
```

Ejecutar ayuda:

```powershell
.\.INVIMA\Scripts\python.exe run_cli.py --help
```

Para instalar tambien las dependencias de la API local:

```powershell
.\.INVIMA\Scripts\python.exe -m pip install -e ".[api]"
```

## Uso basico

Consultar un medicamento en la base local:

```powershell
.\.INVIMA\Scripts\python.exe run_cli.py query PACLITAXEL
```

Generar reporte consolidado:

```powershell
.\.INVIMA\Scripts\python.exe run_cli.py report PACLITAXEL --only-vigente
```

## API local

La API expone la misma logica del reporte CLI como un endpoint HTTP local. Esto permite que una interfaz web consulte la informacion sin leer SQLite directamente.

Arrancar servidor:

```powershell
.\.INVIMA\Scripts\python.exe run_api.py
```

Consultar salud del servicio:

```text
http://127.0.0.1:8000/api/health
```

Consultar reporte de un medicamento:

```text
http://127.0.0.1:8000/api/drugs/PACLITAXEL/report?only_vigente=true
```

Consultar sugerencias para autocompletar la busqueda:

```text
http://127.0.0.1:8000/api/drugs/suggest?q=PAC&limit=10
```

En terminos simples:

- la base SQLite guarda los datos locales;
- la funcion de reporte consulta SQLite y arma un diccionario estructurado;
- FastAPI convierte ese diccionario en JSON;
- el frontend React/Vite llama endpoints de sugerencia y reporte para llenar la ficha visual solo despues de una busqueda.

## Interfaz web local

El frontend vive en `app/` y consulta la API local.

Instalar dependencias:

```powershell
cd app
npm install
```

Arrancar la API desde la raiz del proyecto:

```powershell
.\.INVIMA\Scripts\python.exe run_api.py
```

Arrancar la interfaz:

```powershell
cd app
npm run dev
```

Abrir:

```text
http://127.0.0.1:5173
```

Importar perfil manual oncologico:

```powershell
.\.INVIMA\Scripts\python.exe run_cli.py import-manual "C:\ruta\MEDICAMENTOS ONCOLOGIA.txt" --query PACLITAXEL
```

Importar resultados INVIMA previamente guardados despues de resolver el CAPTCHA manualmente:

```powershell
.\.INVIMA\Scripts\python.exe run_cli.py import-invima-results "C:\ruta\resultado_invima.html" --only-vigente --fetch-details
```

Importar todos los resultados INVIMA guardados en una carpeta:

```powershell
.\.INVIMA\Scripts\python.exe run_cli.py import-invima-results-dir "C:\ruta\resultados_invima" --pattern "*.html" --only-vigente --fetch-details
```

Revisar que medicamentos de la cola manual y UNIRS aun no tienen detalle INVIMA importado:

```powershell
.\.INVIMA\Scripts\python.exe run_cli.py coverage --limit 25
```

Completar detalles desde registros ya importados:

```powershell
.\.INVIMA\Scripts\python.exe run_cli.py fetch-details-from-db PACLITAXEL --only-vigente
```

## Fuentes de informacion

### INVIMA

Fuente primaria para registro sanitario e indicacion regulatoria por producto o presentacion.

El formulario de busqueda principal puede usar CAPTCHA. Este proyecto no implementa bypass, OCR orientado a evasion ni ruptura de controles. El flujo permitido es:

1. busqueda manual por el usuario;
2. resolucion manual del CAPTCHA;
3. guardado de HTML o exportacion tecnica permitida;
4. importacion local;
5. descarga de detalles cuando existen `expediente` y `cdgprod`.

El identificador `cdgprod` debe venir del resultado INVIMA o de una exportacion tecnica equivalente. No debe inferirse desde otras fuentes.

### UNIRS

Fuente complementaria de indicaciones no necesariamente equivalentes a indicacion INVIMA.

### POS Populi

Fuente para cobertura o financiacion con recursos de la Unidad de Pago por Capitacion (UPC).

### Perfil manual oncologico

Fuente curada localmente para mecanismo, clase, eventos adversos, extravasacion, manejo e indicaciones resumidas. No reemplaza a INVIMA, UNIRS ni POS Populi.

### Literatura cientifica

Se usa para completar mecanismo de accion, toxicidad, hipersensibilidad, anafilaxia y manejo cuando el dato no provenga de INVIMA. Debe citarse de forma separada y nunca presentarse como autorizacion regulatoria.

## Orientacion comercial y legal

El codigo puede evolucionar hacia una aplicacion comercial independiente, pero la aplicacion debe conservar atribucion, trazabilidad, separacion de fuentes y una formulacion clara de uso previsto. No debe sugerir aval oficial de INVIMA, Ministerio de Salud, OPS/OMS u otra entidad.

Notas operativas:

- INVIMA, UNIRS y POS Populi conservan la autoridad sobre sus datos oficiales.
- La app no debe reemplazar criterio clinico, revision farmaceutica ni proceso regulatorio.
- Si en el futuro automatiza decisiones clinicas o autorizaciones, debe evaluarse riesgo de software como dispositivo medico.
- Para AIEPI/OPS, el uso comercial de materiales OPS probablemente requiere permiso especifico salvo licencia que permita expresamente uso comercial.

Documentos relacionados:

- `docs/COMMERCIAL_LEGAL_NOTES.md`
- `docs/DATA_SOURCES.md`

## Datos locales y privacidad

Este repositorio no publica la base SQLite local ni archivos descargados o exportados desde fuentes externas. Las carpetas `data/` y `Datos brutos/` estan excluidas por `.gitignore`.

Motivos:

- pueden contener artefactos de sesion o descarga;
- pueden tener restricciones de redistribucion;
- pueden crecer rapidamente;
- deben auditarse antes de ser publicados.

## Pruebas

Ejecutar:

```powershell
.\.INVIMA\Scripts\python.exe -m unittest discover -s tests -v
```

Algunas pruebas usan fixtures locales no incluidos en el repositorio publico. Si esos archivos no existen, se omiten de forma controlada.

Verificacion rapida con API y frontend ya iniciados:

```powershell
.\.INVIMA\Scripts\python.exe scripts\smoke_check.py --drug PACLITAXEL
```

Esta comprobacion valida que la API responda, que el contrato del reporte incluya los campos esperados por la interfaz y que el frontend local devuelva HTTP 200.

## Arquitectura actual

```text
run_cli.py
  -> invima_tool.cli
  -> invima_tool.reporting
  -> parsers / clients / clinical_profiles
  -> SQLite local
  -> JSON operativo

run_api.py
  -> invima_tool.api
  -> invima_tool.reporting
  -> JSON HTTP

app/
  -> React/Vite
  -> GET /api/drugs/{query}/report
  -> ficha visual local
```

Componentes principales:

- `invima_parser.py`: parsea resultados y detalle INVIMA desde HTML.
- `invima_client.py`: consulta experimental de detalle por `expediente + cdgprod`.
- `unirs_parser.py`: lee XLSX de UNIRS.
- `pospopuli_parser.py`: parsea resultados POS Populi desde HTML.
- `manual_parser.py`: extrae perfil manual oncologico.
- `storage.py`: inicializa y actualiza SQLite.
- `reporting.py`: arma el reporte consolidado reusable para CLI/API.
- `clinical_profiles.py`: perfiles de seguridad curados por medicamento cuando existe inmersion cientifica.
- `cli.py`: define comandos de importacion, consulta y reporte.

## Roadmap

1. Procesar progresivamente los medicamentos del documento manual.
2. Procesar medicamentos UNIRS no repetidos despues de terminar la cola manual.
3. Agregar trazabilidad detallada de fuente, fecha y tipo de evidencia.
4. Integrar importadores visuales para INVIMA, manual y fuentes complementarias.
5. Convertir cada inmersion cientifica validada en perfil clinico curado por medicamento.

## Autor

**Martin Munive**  
Medico General. Analista y programador de software.

## Licencia

El codigo del repositorio se distribuye bajo licencia MIT, salvo que un archivo especifico indique otra cosa.
