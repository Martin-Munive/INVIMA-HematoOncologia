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

Estado actual: **prototipo local por CLI**.

Implementado:

- parsers para resultados y detalles INVIMA guardados como HTML;
- parser de UNIRS desde XLSX;
- parser de POS Populi desde HTML guardado;
- parser de documento manual oncologico;
- base local SQLite;
- comandos de importacion, consulta y reporte;
- pruebas unitarias iniciales;
- reporte consolidado funcional para `PACLITAXEL` en el entorno local de desarrollo.

Pendiente:

- API local con FastAPI;
- interfaz web React/Vite inspirada en el estilo de ER-IA;
- ficha visual por medicamento;
- importador de HAR o `Copy as cURL` para flujos post-CAPTCHA;
- trazabilidad ampliada de fuentes y fechas;
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
python -m pip install -e .
```

Ejecutar ayuda:

```powershell
python run_cli.py --help
```

## Uso basico

Consultar un medicamento en la base local:

```powershell
python run_cli.py query PACLITAXEL
```

Generar reporte consolidado:

```powershell
python run_cli.py report PACLITAXEL --only-vigente
```

Importar perfil manual oncologico:

```powershell
python run_cli.py import-manual "C:\ruta\MEDICAMENTOS ONCOLOGIA.txt" --query PACLITAXEL
```

Importar resultados INVIMA previamente guardados despues de resolver el CAPTCHA manualmente:

```powershell
python run_cli.py import-invima-results "C:\ruta\resultado_invima.html" --only-vigente --fetch-details
```

Completar detalles desde registros ya importados:

```powershell
python run_cli.py fetch-details-from-db PACLITAXEL --only-vigente
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

### UNIRS

Fuente complementaria de indicaciones no necesariamente equivalentes a indicacion INVIMA.

### POS Populi

Fuente para cobertura o financiacion con recursos de la Unidad de Pago por Capitacion (UPC).

### Perfil manual oncologico

Fuente curada localmente para mecanismo, clase, eventos adversos, extravasacion, manejo e indicaciones resumidas. No reemplaza a INVIMA, UNIRS ni POS Populi.

### Literatura cientifica

Se usara en una fase posterior para completar mecanismo de accion, toxicidad, hipersensibilidad, anafilaxia y manejo cuando el dato no provenga de INVIMA. Debe citarse de forma separada y nunca presentarse como autorizacion regulatoria.

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
python -m unittest discover -s tests -v
```

Algunas pruebas usan fixtures locales no incluidos en el repositorio publico. Si esos archivos no existen, se omiten de forma controlada.

## Arquitectura actual

```text
run_cli.py
  -> invima_tool.cli
  -> parsers / clients
  -> SQLite local
  -> JSON operativo
```

Componentes principales:

- `invima_parser.py`: parsea resultados y detalle INVIMA desde HTML.
- `invima_client.py`: consulta experimental de detalle por `expediente + cdgprod`.
- `unirs_parser.py`: lee XLSX de UNIRS.
- `pospopuli_parser.py`: parsea resultados POS Populi desde HTML.
- `manual_parser.py`: extrae perfil manual oncologico.
- `storage.py`: inicializa y actualiza SQLite.
- `cli.py`: define comandos de importacion, consulta y reporte.

## Roadmap

1. Crear API local con FastAPI.
2. Exponer `GET /api/drugs/{query}/report`.
3. Crear interfaz React/Vite con estilo visual tipo ER-IA.
4. Mostrar ficha por medicamento con secciones de INVIMA, UNIRS, UPC, perfil manual y fuentes.
5. Agregar trazabilidad detallada de fuente, fecha y tipo de evidencia.
6. Integrar manejo tecnico y toxicidad desde literatura cientifica con citas separadas.
7. Procesar medicamentos adicionales de forma incremental.

## Autor

**Martin Munive**  
Medico General. Analista y programador de software.

## Licencia

El codigo del repositorio se distribuye bajo licencia MIT, salvo que un archivo especifico indique otra cosa.

