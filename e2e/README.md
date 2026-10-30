# E2E: Playwright + Screenplay + pytest-bdd

Automatiza los 3 casos de Azure Test Plans (Catalogo, Carrito, Pedidos) y los casos de borde propuestos con IA.

```
e2e/
├─ features/          Gherkin (keywords en ingles, texto en espanol)
│  ├─ catalogo.feature   @TC20  Filtrar por categoria
│  ├─ carrito.feature    @TC19  Agregar al carrito (2 escenarios)
│  ├─ pedidos.feature    @TC21  Confirmar pedido
│  └─ bordes.feature     @ia    3 casos de borde (ver docs/prompt-ia.md)
├─ screenplay/        Patron Screenplay: actor, abilities, interactions, tasks, questions
├─ tests/             steps_comunes.py + test_*.py (enlazan features con steps)
├─ tools/             publicar_test_plan.py (resultados -> Test Points de Azure)
├─ docs/              casos manuales de Azure Test Plans + prompt de IA
├─ conftest.py        fixtures, evidencia Allure (captura por paso, video, trace) y tag @TC -> JUnit
└─ requirements.txt   playwright, pytest, pytest-bdd, allure-pytest-bdd...
```

## Correr en local

La app debe estar corriendo en `http://localhost:3000` (ver el README de la raiz).

```bash
cd e2e
python -m venv .venv
# Windows:  .venv\Scripts\activate      Linux/macOS:  source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
pytest                                   # todos los escenarios (7)
pytest -m "not ia"                       # solo los 4 de los casos manuales
pytest -m ia                             # solo los 3 casos de borde
```

Contra otra URL (Fase 4): `BASE_URL=https://mi-app pytest` (Windows: `$env:BASE_URL="https://mi-app"; pytest`).

Genera `resultados/junit.xml` si agregas `--junitxml=resultados/junit.xml -o junit_family=xunit2`.

## Fase 4: ejecucion remota en Sauce Labs

El proyecto incluye una modalidad de **demo guiada** para cuando no se dispone de una cuenta. La configuracion remota esta en `sauce/` y el ejecutor en `tools/ejecutar_sauce.py`; no contiene credenciales ni inicia sesiones remotas por defecto.

```powershell
# Evidencia de configuracion sin requerir una cuenta Sauce Labs
.\.venv\Scripts\python.exe tools\ejecutar_sauce.py --demo
```

Guarda una captura del resultado junto con el documento de soporte, fuera del repositorio. Para activar una cuenta real, revisa [`sauce/README.md`](sauce/README.md): usa las variables secretas `SAUCE_USERNAME` y `SAUCE_ACCESS_KEY`, una `SAUCE_BASE_URL` publica o Sauce Connect, y marca el parametro `runSauce` en Azure Pipelines.
