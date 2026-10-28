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
