# Escenarios con IA: Claude + servidor MCP de Playwright (Fase 3)

La fase pide usar **Claude con el servidor MCP de Playwright** para generar o mantener al menos 1 escenario
nuevo y **documentar el prompt**. Este archivo guarda el prompt y el registro de la sesion.

## Preparacion

1. Claude Desktop con el MCP de Playwright: pega el bloque `mcpServers` de `mcp-claude-ejemplo.json` en
   **Settings > Developer > Edit Config**, cierra Claude por completo y vuelve a abrirlo.
2. Deja la tienda corriendo en `http://localhost:3000` (`npm start` en `app-tienda/`).

## Prompt 1 - generar casos de borde

```
Eres un ingeniero de QA. Usa el servidor MCP de Playwright para abrir http://localhost:3000 y explorar la
tienda: catalogo, filtro por categoria, buscador, detalle de producto, carrito y confirmacion de pedido.

Ya tengo automatizados estos escenarios (no los repitas):
- Filtrar el catalogo por la categoria "hogar"
- Agregar un producto al carrito / agregar dos productos distintos
- Confirmar un pedido con un producto

Propon 3 casos de borde que aporten cobertura nueva. Para cada uno entrega:
1. El riesgo que cubre, en una linea.
2. El escenario en Gherkin (keywords en ingles, texto en espanol), reutilizando EXACTAMENTE estos pasos:
   - Given que abro la home de la tienda
   - When filtro el catalogo por la categoria "<categoria>"
   - When busco el producto "<texto>"
   - When agrego el producto <n> al carrito
   - When abro el carrito
   - When abro el carrito y confirmo el pedido con el correo "<correo>"
   - Then solo veo productos de la categoria "<categoria>"
   - Then la cantidad de productos visibles es mayor que cero
   - Then el contador del carrito muestra <n>
   - Then veo el mensaje de que no hay productos para el filtro
   - Then veo el mensaje de carrito vacio
   - Then el carrito lista <n> producto distinto
   - Then veo el mensaje de pedido confirmado
   - Then el numero de pedido no esta vacio
   Si necesitas un paso nuevo, marcalo y dime que Task o Question de Screenplay haria falta.
3. Lo que observaste en el navegador (data-testid usados). Verifica cada caso en la app antes de proponerlo.
```

## Prompt 2 - mantener un escenario (ejemplo)

```
En el front, el boton con data-testid="confirmar-pedido" ahora se llama "finalizar-pedido".
Revisa e2e/screenplay/tasks.py y dime que lineas cambiar para que el escenario "Confirmar un pedido con un
producto" siga en verde. No toques nada mas.
```

## Registro de la sesion (completar tras ejecutarla)

| Campo | Valor |
|-------|-------|
| Fecha | _completar_ |
| Cliente / modelo | Claude Desktop + MCP `@playwright/mcp` / _completar modelo_ |
| Prompt usado | Prompt 1 (o el que hayas usado; pegalo aqui tal cual) |
| Escenarios propuestos por la IA | _completar_ |
| Cambios que hice yo tras revisarlos | _completar_ |
| Captura de la sesion | `docs/evidencias/fase3-prompt-ia.png` (agregar) |

## Estado de `features/bordes.feature`

Los 3 escenarios de `bordes.feature` (busqueda sin resultados, carrito vacio, mismo producto dos veces) son un
**borrador de partida redactado con apoyo de Claude a partir del codigo del front, sin el MCP**. Para cumplir la
fase con evidencia real: ejecuta el Prompt 1, compara lo que propone con este borrador, ajusta el feature con lo
que valides y guarda la captura. Declaralo asi en el documento de soporte.

## Cosas para explorar con el MCP

- El front no valida el formato del correo: con el campo vacio usa `cliente@test.com` por defecto.
- La API no descuenta stock al crear un pedido.
