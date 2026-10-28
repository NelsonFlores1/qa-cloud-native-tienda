# Casos manuales en Azure Test Plans (Fase 3)

Los 3 casos se crean **a mano** en Azure Test Plans (pasos + resultado esperado). Al automatizarlos se
traducen a Gherkin (carpeta `features/`) y el resultado se publica de vuelta al plan gracias al tag `@TC<id>`.

## 1. Crear el plan

1. Azure DevOps > **Test Plans** > **New Test Plan** > nombre: `Tienda v1 - Regresion`.
2. Dentro del plan, crea un suite (por ejemplo `Regresion Tienda`) y agrega los 3 Test Cases ahi.
3. Abre cada Test Case y anota su **ID** (el numero junto al titulo).

## 2. Los 3 Test Cases (copiar y pegar en el portal)

### Caso "Catalogo" - Filtrar productos por categoria Hogar

| # | Accion | Resultado esperado |
|---|--------|--------------------|
| 1 | Abrir la home de la tienda (`http://localhost:3000`) | Se muestra el catalogo con productos |
| 2 | En el filtro **Categoria** elegir **Hogar** | El catalogo se actualiza |
| 3 | Revisar las tarjetas visibles | Todas son de la categoria hogar y hay al menos un producto |

Automatizado en: `features/catalogo.feature` (tag `@TC<id del caso Catalogo>`)

### Caso "Carrito" - Agregar un producto al carrito

| # | Accion | Resultado esperado |
|---|--------|--------------------|
| 1 | Abrir la home de la tienda | Se muestra el catalogo y el carrito marca 0 |
| 2 | Pulsar **Agregar al carrito** en el producto 1 | El contador del carrito muestra **1** |

Automatizado en: `features/carrito.feature` (tag `@TC<id del caso Carrito>`)

### Caso "Pedidos" - Confirmar un pedido con un producto

| # | Accion | Resultado esperado |
|---|--------|--------------------|
| 1 | Abrir la home y agregar el producto 1 al carrito | El contador del carrito muestra 1 |
| 2 | Abrir el carrito | Se ve el producto y el formulario de contacto |
| 3 | Escribir el correo `ana@tienda-qa.com` y pulsar **Confirmar pedido** | Aparece "Pedido confirmado" con un numero de pedido no vacio |

Automatizado en: `features/pedidos.feature` (tag `@TC<id del caso Pedidos>`)

## 3. Enlazar los IDs con el codigo

Los features traen los IDs del ejemplo de clase (`@TC19`, `@TC20`, `@TC21`). **Reemplazalos por los IDs de tus
Test Cases**:

```
features/catalogo.feature  ->  @TC20  por  @TC<tu id del caso Catalogo>
features/carrito.feature   ->  @TC19  por  @TC<tu id del caso Carrito>
features/pedidos.feature   ->  @TC21  por  @TC<tu id del caso Pedidos>
```

El `conftest.py` lee ese tag y lo escribe en el `junit.xml` como `test_case_id`; Azure usa ese ID para enlazar
el resultado automatizado con el Test Case.

## 4. Publicar los resultados en el plan (desde el pipeline)

1. En `pipeline/azure-pipelines.yml` completa `TEST_PLAN_ID` y `TEST_SUITE_ID` (los ves en la URL de Test Plans:
   `.../_testPlans/execute?planId=XX&suiteId=YY`).
2. Crea un **PAT** (User settings > Personal Access Tokens) con permiso **Test Management (Read & write)**.
3. En el pipeline: **Edit > Variables > New variable**: nombre `AZURE_DEVOPS_PAT`, valor el token, marca
   **Keep this value secret**.
4. Al correr el pipeline, el stage `E2E` publica el JUnit (pestana **Tests**) y `tools/publicar_test_plan.py`
   mueve los Test Points a Passed/Failed (pestana **Execute** del plan).
