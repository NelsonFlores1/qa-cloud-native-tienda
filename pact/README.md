# Fase 5 - Contract testing con Pact

Este contrato protege la integracion entre el consumidor **TiendaWeb** y el proveedor **TiendaApi** para `GET /api/productos`.

## Que se pacta

- El consumidor solicita `GET /api/productos` con `Accept: application/json`.
- El proveedor responde `200` y `Content-Type: application/json; charset=utf-8`.
- La respuesta es una lista no vacia de productos con `id`, `nombre`, `categoria`, `descripcion`, `precio` y `stock`.

## Ejecutar en local

Desde la raiz del repositorio:

```powershell
cd datos
npm ci
npm run generar
cd ..\pact
npm install
npm test
```

La primera parte genera `pacts/TiendaWeb-TiendaApi.json` mediante un mock de Pact. La segunda inicia la API real en el puerto 3100 y verifica ese contrato contra ella. El resultado esperado termina con:

```text
PACT PROVIDER VERIFIED: TiendaApi cumple GET /api/productos.
```

## Imagen Docker

Desde la raiz del repositorio:

```powershell
docker build -t tienda-qa:local .
docker run -d --name tienda-qa-fase5 -p 3000:3000 tienda-qa:local
docker inspect --format='{{.State.Health.Status}}' tienda-qa-fase5
Invoke-RestMethod http://localhost:3000/api/health
docker stop tienda-qa-fase5
docker rm tienda-qa-fase5
```

El Dockerfile genera `db.json` dentro de la imagen y usa `/api/health` como `HEALTHCHECK`.

## ACR preparado para una cuenta real

El pipeline incluye el stage opcional `PublishAcr`. Solo se ejecuta con `publishAcr=true` y requiere:

- una suscripcion o service connection de Azure en `AZURE_SUBSCRIPTION`;
- el nombre del registro en `ACR_NAME`;
- permisos para ejecutar `az acr build`.

Nunca versionar credenciales de Azure ni de un registro. La publicacion puede permanecer como demo guiada si no se dispone de una suscripcion.

Referencia: [Pact JS](https://docs.pact.io/implementation_guides/javascript/readme) y [verificacion de provider](https://docs.pact.io/implementation_guides/javascript/docs/provider/).
