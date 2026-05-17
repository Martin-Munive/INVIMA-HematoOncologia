# Fuentes y trazabilidad

## Proposito

Este documento define como debe interpretarse cada fuente dentro de `INVIMA-HematoOncologia`.

## Principio central

No todas las fuentes tienen la misma autoridad.

Una indicacion solo puede mostrarse como **INVIMA** si fue extraida de una fuente INVIMA real. Otras fuentes pueden complementar, contrastar o enriquecer la ficha, pero no reemplazan la autoridad regulatoria.

## Jerarquia operativa

1. **INVIMA**: fuente primaria para registro sanitario, estado regulatorio e indicacion por producto o presentacion.
2. **POS Populi**: fuente de cobertura o financiacion UPC.
3. **UNIRS**: fuente complementaria de indicaciones.
4. **Perfil manual oncologico**: fuente curada local para mecanismo, seguridad, extravasacion e indicaciones resumidas.
5. **Literatura cientifica**: fuente futura para completar mecanismo, toxicidad, hipersensibilidad, anafilaxia y manejo, siempre con cita separada.

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

