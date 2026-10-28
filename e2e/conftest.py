"""Configuracion compartida de pytest para las pruebas E2E.

Fixtures:
  - base_url     : URL de la app (local por defecto, configurable con BASE_URL)
  - actor        : un Actor Screenplay con la habilidad de navegar

Evidencia (Allure):
  - Tras CADA paso Gherkin se adjunta una captura de la pagina -> queda el
    "paso a paso visual" de por donde paso la prueba en la app.
  - Si un paso FALLA, se adjunta captura + el HTML de la pagina.
  - Al terminar cada escenario se adjunta el VIDEO y el TRACE de Playwright
    (el trace se abre con `playwright show-trace` y es navegable paso a paso).

Tambien reinicia los pedidos antes de cada prueba (endpoint /api/test/reset).
"""
import os
import sys
from pathlib import Path

import pytest
import requests

# Permite importar el paquete screenplay/ sin instalarlo
sys.path.insert(0, str(Path(__file__).parent))

from screenplay.actor import Actor
from screenplay.abilities import NavegarConElNavegador

# Allure es opcional: si no esta instalado, las pruebas corren igual (sin adjuntos).
try:
    import allure
    from allure_commons.types import AttachmentType
    _ALLURE = True
except ImportError:  # pragma: no cover
    _ALLURE = False


def pytest_addoption(parser):
    parser.addoption(
        "--base-url-tienda",
        action="store",
        default=None,
        help="URL base de la app Tienda (ej. http://localhost:3000)",
    )


@pytest.fixture(scope="session")
def base_url(request):
    # Prioridad: flag de linea de comandos > variable de entorno > local
    return (
        request.config.getoption("--base-url-tienda")
        or os.environ.get("BASE_URL")
        or "http://localhost:3000"
    )


# ── Playwright: activar video y trace ──────────────────────────────
# pytest-playwright permite configurar el contexto del navegador.
# Grabamos video de toda la sesion y habilitamos el trace (snapshots +
# screenshots internos) que luego adjuntamos a Allure.
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    carpeta_video = Path(__file__).parent / "resultados" / "videos"
    carpeta_video.mkdir(parents=True, exist_ok=True)
    return {
        **browser_context_args,
        "record_video_dir": str(carpeta_video),
        "viewport": {"width": 1280, "height": 720},
    }


@pytest.fixture
def context(context):
    """Inicia el trace de Playwright al abrir el contexto."""
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield context
    # el trace se detiene y adjunta en el fixture `page` (necesita la page viva)


@pytest.fixture(autouse=True)
def _reset_pedidos(base_url):
    """Deja los pedidos en limpio antes de cada escenario (si la app lo soporta)."""
    try:
        requests.post(f"{base_url}/api/test/reset", timeout=3)
    except requests.RequestException:
        pass  # si no esta disponible, seguimos; no es critico
    yield


# ── Enlace con Azure Test Plans (Test Case ID) ─────────────────────
# Cada escenario Gherkin lleva un tag @TC<id> (ej. @TC123) con el ID del
# Test Case de Azure. Este hook lee ese tag y lo escribe en el JUnit como
# una propiedad del testcase. Al publicar con PublishTestResults@2, Azure
# usa ese ID para enlazar el resultado automatizado con el caso manual y
# marcarlo Passed/Failed en el Test Plan.
import re as _re

_TC_RE = _re.compile(r"^TC(\d+)$", _re.IGNORECASE)


def _extraer_test_case_id(tags):
    for t in tags or []:
        m = _TC_RE.match(str(t))
        if m:
            return m.group(1)
    return None


def pytest_bdd_before_scenario(request, feature, scenario):
    """Antes de cada escenario: si tiene tag @TC<id>, lo registra en el JUnit."""
    tc_id = _extraer_test_case_id(getattr(scenario, "tags", None))
    if not tc_id:
        return
    # Propiedad a nivel de testcase que Azure DevOps lee como Test Case ID.
    try:
        record_property = request.getfixturevalue("record_property")
        record_property("test_case_id", tc_id)
    except Exception:
        pass
    # Tambien lo marcamos en Allure como enlace al caso (si esta disponible).
    if _ALLURE:
        try:
            allure.dynamic.label("testcase_id", tc_id)
            allure.dynamic.tag(f"TC{tc_id}")
        except Exception:
            pass


@pytest.fixture
def actor(page, base_url) -> Actor:
    """Un actor llamado Ana que puede navegar con el navegador de Playwright."""
    actor = Actor.llamado("Ana").que_puede(
        NavegarConElNavegador.usando(page, base_url)
    )
    yield actor
    # ── Al terminar el escenario: adjuntar trace y video a Allure ──
    if not _ALLURE:
        return
    resultados = Path(__file__).parent / "resultados"
    # Trace (navegable con playwright show-trace)
    try:
        traza = resultados / "trace-ultimo.zip"
        page.context.tracing.stop(path=str(traza))
        if traza.exists():
            allure.attach(
                traza.read_bytes(),
                name="trace-playwright.zip",
                extension="zip",
            )
    except Exception:
        pass
    # Video (se escribe al cerrar la page)
    try:
        video = page.video
        page.close()  # fuerza el guardado del video
        if video:
            ruta_video = Path(video.path())
            if ruta_video.exists():
                allure.attach(
                    ruta_video.read_bytes(),
                    name="video-sesion.webm",
                    attachment_type=AttachmentType.WEBM,
                )
    except Exception:
        pass


# ── Hooks de pytest-bdd: capturas por paso y en fallo ──────────────
def _captura(page, nombre):
    if not _ALLURE:
        return
    try:
        allure.attach(
            page.screenshot(full_page=True),
            name=nombre,
            attachment_type=AttachmentType.PNG,
        )
    except Exception:
        pass


def _buscar_page(step_func_args):
    """Encuentra la Page a partir de los argumentos del step (via actor)."""
    actor = step_func_args.get("actor")
    if actor is not None:
        try:
            return actor.habilidad(NavegarConElNavegador).page
        except Exception:
            return None
    return step_func_args.get("page")


def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args):
    """Tras CADA paso OK: adjunta una captura con el texto del paso."""
    page = _buscar_page(step_func_args)
    if page is not None:
        _captura(page, f"{step.keyword} {step.name}")


def pytest_bdd_step_error(
    request, feature, scenario, step, step_func, step_func_args, exception
):
    """Si un paso FALLA: adjunta captura + el HTML de la pagina."""
    page = _buscar_page(step_func_args)
    if page is None or not _ALLURE:
        return
    _captura(page, f"FALLO en: {step.keyword} {step.name}")
    try:
        allure.attach(
            page.content(),
            name="html-de-la-pagina.html",
            attachment_type=AttachmentType.HTML,
        )
    except Exception:
        pass
