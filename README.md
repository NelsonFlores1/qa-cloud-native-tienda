# Reto practico - Modulo 5: QA Cloud-Native, Automatizacion Inteligente con IA Generativa


Proyecto sobre la **app Tienda** (front SPA + API REST en Node/Express): datos de prueba reproducibles, pipeline
CI/CD en Azure con quality gates, y automatizacion E2E con Playwright + Screenplay + BDD asistida por IA.

## Estado de las fases

| Fase | Entregable | Donde | Estado |
|------|-----------|-------|--------|
| 1 - Datos de prueba realistas | `generar-datos.js` con semilla fija + `db.json` generado (+ anonimizacion, reto extra) | [`datos/`](datos) | Hecho |
| 2 - Pipeline CI/CD con quality gates | `azure-pipelines.yml` con build, smoke, carga, E2E, contenedor, contrato, ACR y deploy simulado | [`pipeline/`](pipeline) | Hecho |
| 3 - Del caso manual al automatizado con IA | Features, steps, Screenplay, casos de borde, enlace a Test Plans | [`e2e/`](e2e) | Hecho |
| 4 - Ejecucion en la nube (Sauce Labs) | Demo guiada: configuracion remota, stage opcional y evidencia sin credenciales | `e2e/sauce/` + `e2e/tools/ejecutar_sauce.py` + `pipeline/` | Hecho como demo guiada |
| 5 - Contenedores y contract testing | Dockerfile, healthcheck, contrato Pact e imagen publicada en ACR | raiz, `pact/` y `pipeline/` | Hecho; imagen `tienda-qa` publicada en ACR |
| 6 - Metricas y estrategia | DORA, piramide de pruebas y riesgos | este README y el documento de soporte | Hecho |

## Estructura del repositorio

```
.
├─ app-tienda/        La app bajo prueba (front en public/, API en servidor/)
├─ datos/             Generador de datos (Faker + semilla fija) y anonimizacion
│  ├─ generar-datos.js          Fase 1: produce app-tienda/datos/db.json
│  ├─ anonimizar.js             Reto extra: anonimiza el dump ficticio
│  ├─ dump-real-ficticio.json   "Dump real" ficticio con datos personales inventados
│  └─ verificar-reproducibilidad.js   Genera dos veces y compara el hash
├─ e2e/               Playwright + Screenplay + pytest-bdd (ver e2e/README.md)
├─ pipeline/          azure-pipelines.yml con stages y gates; tests/ de smoke y carga
├─ Dockerfile         Fase 5: imagen reproducible y healthcheck
├─ pact/              Fase 5: contrato Consumer TiendaWeb - Provider TiendaApi
└─ README.md
```

## Requisitos

- **Node.js 20+** y npm
- **Python 3.11+** (solo para el E2E)
- Git

## Como correr todo en local

Desde la raiz del repo. Las variables de entorno se muestran para PowerShell (Windows) y bash.

**1. Generar los datos (Fase 1)**

```bash
cd datos
npm install            # instala Faker en version exacta (9.9.0)
npm run generar        # escribe app-tienda/datos/db.json
npm run verificar      # genera dos veces y compara el hash SHA-256: deben coincidir
npm run anonimizar     # (opcional) muestra el antes/despues de la anonimizacion
cd ..
```

**2. Levantar la app**

```bash
cd app-tienda
npm install
npm start              # http://localhost:3000   (salud: /api/health)
```

Deja esa terminal abierta y usa otra para los pasos siguientes.

**3. Smoke test y prueba de carga (Fase 2)**

```bash
cd pipeline
npm run smoke          # 7 comprobaciones: salud, catalogo, producto, 404, filtro, front, crear pedido
npm run carga          # p95 < 800 ms y error < 1 %; sale con codigo 1 si no cumple
```

Forzar el gate de carga en ROJO (SLA imposible):

```powershell
$env:SLA_P95_MS=1; npm run carga      # PowerShell
```
```bash
SLA_P95_MS=1 npm run carga            # bash
```

**4. E2E (Fase 3)**

```bash
cd e2e
python -m venv .venv
# Windows: .venv\Scripts\activate     Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
pytest
```

Detalle de features, Screenplay y los prompts de IA en [`e2e/README.md`](e2e/README.md).

**5. Configuracion remota guiada (Fase 4)**

La configuracion remota queda preparada sin guardar credenciales en el repositorio. Este comando muestra el
endpoint, las capabilities y la URL que se usarian en Sauce Labs, sin abrir una sesion remota:

```powershell
cd e2e
.\.venv\Scripts\python.exe tools\ejecutar_sauce.py --demo
cd ..
```

En local, Playwright abre el navegador en el equipo y usa `http://localhost:3000`. Para Sauce Labs se conservan
los mismos escenarios, pero se usa una URL publica o un tunel, capabilities de navegador y las variables seguras
`SAUCE_USERNAME` y `SAUCE_ACCESS_KEY`.

**6. Contenedor y contrato Pact (Fase 5)**

```powershell
# Desde la raiz: genera db.json DENTRO de la imagen y expone /api/health
docker build -t tienda-qa:local .
docker run -d --name tienda-qa-fase5 -p 3000:3000 tienda-qa:local
docker inspect --format='{{.State.Health.Status}}' tienda-qa-fase5
Invoke-RestMethod http://localhost:3000/api/health
docker stop tienda-qa-fase5
docker rm tienda-qa-fase5

# Contrato: genera el pact y lo verifica contra la API real
cd datos; npm ci; npm run generar; cd ..\pact
npm ci
npm test
```

El contrato resultante queda en `pact/pacts/TiendaWeb-TiendaApi.json`. La guia de ACR y las evidencias requeridas estan en [`pact/README.md`](pact/README.md).

**7. Publicar la imagen en ACR desde el pipeline**

En Azure DevOps, ejecuta el pipeline y activa el parametro `publishAcr`. La conexion de servicio debe apuntar a la
suscripcion correcta, y la identidad de la conexion necesita el rol `AcrPush` sobre el registro. El stage
`AcrPublication` construye la imagen en el agente y la publica como:

```text
<nombre-del-registro>.azurecr.io/tienda-qa:<numero-de-build>
```

La corrida final de esta practica publico una imagen en el repositorio `tienda-qa` de ACR.

## Pipeline en Azure DevOps (Fase 2 y 3)

```
Build -> SmokeTests -> LoadTest -> E2E -> CloudE2E -> Container -> ContractTests -> AcrPublication -> Deploy (simulado)
           GATE 1       GATE 2    GATE 3                 GATE 4       GATE 5
```

| Gate | Stage | Que valida | Como detiene el deploy |
|------|-------|-----------|------------------------|
| 1 | `SmokeTests` | La app encendio: health, catalogo, crear pedido (`pipeline/tests/smoke-api.js`) | `exit 1` si algo falla |
| 2 | `LoadTest` | SLA: p95 < 800 ms y error < 1 % (`pipeline/tests/carga-simple.js`) | `exit 1` si no cumple |
| 3 | `E2E` | Escenarios Gherkin en verde (`pytest`) | pytest sale con codigo != 0 |
| 4 | `Container` | La imagen responde en `/api/health` | falla el healthcheck del contenedor |
| 5 | `ContractTests` | Contrato Pact de `GET /api/productos` | consumer o provider termina con error |

Cada stage depende del anterior y `Deploy` solo corre si todos terminaron bien.

**Conectar el repo:** Azure DevOps > Pipelines > New pipeline > **GitHub** > autoriza la app de Azure Pipelines >
elige este repo > *Existing Azure Pipelines YAML file* > `/pipeline/azure-pipelines.yml`. El pipeline se dispara en
cada push a `main`.

**Demostrar el gate en rojo y en verde:** *Run pipeline* con los valores por defecto (800 ms / 1 %) = verde.
*Run pipeline* con **SLA p95 = 1** = `LoadTest` en rojo y `E2E`/`Deploy` omitidos. No se toca el codigo: el SLA es
un parametro.

**Publicar en Azure Test Plans (Fase 3):** crea los 3 Test Cases, pon sus IDs en los tags `@TC` de los features,
completa `TEST_PLAN_ID` / `TEST_SUITE_ID` en el YAML y crea la variable secreta `AZURE_DEVOPS_PAT`. Pasos
detallados en [`e2e/docs/azure-test-plans-casos.md`](e2e/docs/azure-test-plans-casos.md).

## Decisiones tecnicas

**Por que NO se versiona `db.json` (Fase 1).**
1. Es un artefacto derivado: se regenera siempre desde el script y la semilla, que son la fuente de verdad.
2. Evita ruido y conflictos en Git: cada cambio del generador produciria diffs enormes en un JSON que nadie edita.
3. Evita que se desincronice: si cambia el script y alguien olvida regenerar el archivo, el repo tendria datos que
   no corresponden al codigo.
4. El pipeline parte de un estado limpio: lo genera en cada corrida y la semilla fija garantiza tests deterministas.

**Datos reproducibles en toda maquina.** Semilla fija (`faker.seed(2025)`) **y** version exacta de Faker (9.9.0, con
su `package-lock.json`): con una version distinta la misma semilla podria dar otros datos. `npm run verificar`
lo comprueba comparando hashes.

**Datos coherentes.** Los 24 productos se reparten en las 4 categorias del front (hogar, tecnologia, ropa,
juguetes). Nombre, descripcion, rango de precio y rango de stock salen de la misma configuracion de categoria.

**Anonimizacion (reto extra).** Se parte de `dump-real-ficticio.json` (10 clientes inventados con nombre, correo
y telefono) y `anonimizar.js` los reemplaza por pseudonimos con SHA-256 + sal: mismo cliente, mismo pseudonimo, sin
vuelta al dato original. El telefono se descarta. El script verifica que ningun dato personal original llegue a
`db.json`.

**Cada stage repite la preparacion de la app.** Cada stage corre en un agente efimero y la app muere al terminar
el stage, asi que `pipeline/templates/preparar-app.yml` genera los datos, instala y arranca la app en cada uno.

**Screenplay + BDD.** Los features estan en Gherkin con keywords en ingles y texto en espanol; los steps solo
llaman a *tasks* y *questions* del actor, de modo que las pruebas se leen como negocio y los selectores viven en un
solo lugar.

## Declaracion honesta: que corre de verdad y que es demo guiada

| Parte | Condicion |
|-------|-----------|
| Generacion de datos, anonimizacion, smoke, carga y E2E | Corren de verdad en local y en el agente de Azure Pipelines |
| Conexion GitHub > Azure Pipelines, Test Plans, PAT | Se configuran en los portales; la evidencia son capturas de la cuenta real |
| Stage `Deploy` | **Simulado**: solo imprime un mensaje, no despliega nada |
| Sauce Labs (Fase 4) | **Demo guiada implementada**: capacidades remotas, ejecutor por variables y stage `CloudE2E` desactivado por defecto. Falta una cuenta, secretos y una URL accesible para una ejecucion remota real. |
| Docker y Pact (Fase 5) | **Implementados**: Dockerfile genera los datos dentro de la imagen, verifica `/api/health` y Pact valida `GET /api/productos` entre consumidor y provider. |
| ACR / App Service (Fase 5) | La imagen se publico de verdad en ACR mediante `AcrPublication`. El stage usa `docker push`; necesita `AZURE_SUBSCRIPTION`, `ACR_NAME`, el rol `AcrPush` y ejecutar `publishAcr=true`. App Service no se desplego. |

**Casos de borde con IA (Fase 3).** El archivo `e2e/features/bordes.feature` incluye casos de borde preparados a
partir del codigo del front. El prompt y la guia de registro estan en
[`e2e/docs/prompt-ia.md`](e2e/docs/prompt-ia.md); la captura se conserva con el documento de soporte, fuera del repositorio.

**Uso de IA.** El proyecto parte de los ejemplos de clase (app Tienda, generador de datos, `smoke-api.js`,
`carga-simple.js`, framework E2E y pipeline de la Sesion 3 y 4) y se adapto con apoyo de Claude (Anthropic).

## Cuadro de metricas DORA y piramide de pruebas (Fase 6)

Estas metricas son una linea base de la practica. Aun no hay trafico ni incidentes de produccion, por eso se
distingue lo observado en el pipeline de lo que deberia medirse cuando la aplicacion tenga operacion real.

| Metrica | Linea base | Siguiente medicion |
|---|---|---|
| Frecuencia de despliegue | Una imagen publicada en ACR (`tienda-qa`, tag del build). | Contar cada publicacion que supere todos los gates. |
| Lead time de cambio | El pipeline conserva el commit, el numero de build y los tiempos de cada etapa. | Medir desde el commit hasta el tag publicado en ACR. |
| Tasa de fallos de cambio | No hubo despliegue productivo; los fallos detectados fueron de CI y se corrigieron antes de la corrida final. | Separar fallos de CI de fallos posteriores a produccion. |
| MTTR | No aplica aun porque no se registraron incidentes de produccion. | Medir desde la deteccion hasta recuperar el servicio. |

```text
                  E2E
        Playwright + pytest-bdd
              7 escenarios

        Contrato e integracion
     Pact + smoke API + prueba de carga

              Unitarias
  Generador, carrito y validaciones
  Siguiente paso: ampliar esta base
```

Las pruebas E2E validan el recorrido completo. Pact, smoke y carga comprueban la comunicacion entre componentes.
La base unitaria debe crecer para detectar antes las reglas simples.

### Riesgos y como reducirlos

| Riesgo | Como se reduce |
|---|---|
| Dependencia de servicios cloud | La publicacion usa `docker push` y la conexion tiene el rol `AcrPush`. |
| Pocas pruebas unitarias | Agregar pruebas para el generador, validaciones y calculos de carrito. |
| Metricas sin produccion | Mantenerlas como linea base y registrar eventos reales cuando exista un entorno productivo. |
| Ejecucion remota opcional | Mantener la demo guiada y activar Sauce Labs solo con cuenta, secretos y URL accesible. |

## Creditos

App Tienda y materiales base: Lite Thinking Institute of Technology (Diplomado, Modulo 5).
