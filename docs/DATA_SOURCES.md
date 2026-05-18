# Fuentes y trazabilidad

## Proposito

Este documento define como debe interpretarse cada fuente dentro de `INVIMA-HematoOncologia`.

## Principio central

No todas las fuentes tienen la misma autoridad.

Una indicacion solo puede mostrarse como **INVIMA** si fue extraida de una fuente INVIMA real. Otras fuentes pueden complementar, contrastar o enriquecer la ficha, pero no reemplazan la autoridad regulatoria.

## Regla de adopcion de fuentes nuevas

Toda fuente nueva que pueda cambiar una conclusion regulatoria, clinica, de cobertura o comercial activa `LINTERNA` antes de implementarse como fuente primaria.

Antes de programar contra esa fuente debe quedar respondido:

1. Que fuente es y quien la publica.
2. Si es oficial, secundaria, espejo, archivo historico o fuente privada.
3. Que campos contiene y que campos no contiene.
4. Frecuencia de actualizacion o evidencia disponible de vigencia.
5. Licencia, terminos de uso y restricciones de automatizacion.
6. Diferencias frente a la consulta web INVIMA.
7. Riesgo de datos incompletos o desactualizados.
8. Decision propuesta: adoptar, adoptar como complementaria, usar solo para contraste, investigar mas o rechazar.

La adopcion como fuente primaria requiere aprobacion explicita del usuario. Hasta entonces debe tratarse como candidata.

## Jerarquia operativa

1. **INVIMA**: fuente primaria para registro sanitario, estado regulatorio e indicacion por producto o presentacion.
2. **POS Populi**: fuente de cobertura o financiacion UPC.
3. **UNIRS**: fuente complementaria de indicaciones.
4. **Perfil manual oncologico**: fuente curada local para mecanismo, seguridad, extravasacion e indicaciones resumidas.
5. **Literatura cientifica**: fuente futura para completar mecanismo, toxicidad, hipersensibilidad, anafilaxia y manejo, siempre con cita separada.

## Fuente candidata: Datos Abiertos CUM de INVIMA

Estado: candidata, pendiente de comparacion tecnica contra la consulta web por medicamento antes de adopcion primaria.

Hallazgo preliminar:

- El portal Datos Abiertos Colombia publica datasets atribuidos a INVIMA para Codigo Unico de Medicamentos.
- La fuente puede servir para escalar registros, estados, productos, titulares y presentaciones sin guardar manualmente una pagina por medicamento.
- Aun no debe asumirse que contiene todas las indicaciones clinicas detalladas que aparecen en la consulta web por presentacion.
- Debe compararse contra PACLITAXEL y GOSERELINA antes de reemplazar el flujo HTML post-CAPTCHA.

Decision provisional:

- usarla solo como fuente candidata de investigacion;
- no declarar completitud INVIMA desde ella hasta validar campos, actualizacion y concordancia;
- conservar la consulta web/detalle por expediente como fuente de indicaciones si Datos Abiertos no las contiene.

## Regla de seguridad

El sistema no debe automatizar bypass de CAPTCHA ni ruptura de controles de acceso.

Flujo permitido para INVIMA:

1. el usuario consulta manualmente;
2. el usuario resuelve CAPTCHA;
3. el usuario guarda HTML o exporta una solicitud permitida;
4. el sistema importa y estructura la informacion;
5. el sistema declara fuente y limite.

## Datos excluidos del repositorio

No se publican por defecto:

- `data/`;
- `Datos brutos/`;
- bases SQLite;
- HTML descargado;
- XLSX de terceros;
- archivos exportados desde sesiones web.

Estos archivos pueden usarse localmente, pero requieren auditoria antes de cualquier publicacion.
