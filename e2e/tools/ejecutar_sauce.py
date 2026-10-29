"""Ejecuta la suite E2E en Sauce Labs sin cambiar los escenarios.

Modo demo guiada:
    python tools/ejecutar_sauce.py --demo

Modo remoto real (solo cuando existan credenciales y una URL accesible):
    SAUCE_USERNAME=... SAUCE_ACCESS_KEY=... SAUCE_BASE_URL=https://... \
    python tools/ejecutar_sauce.py

pytest-playwright reconoce SELENIUM_REMOTE_URL y
SELENIUM_REMOTE_CAPABILITIES. Sauce Labs utiliza esa conexion Selenium Grid
para iniciar Chrome o Edge remoto y Playwright se conecta por CDP.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


ENDPOINTS = {
    "us-west-1": "https://ondemand.us-west-1.saucelabs.com:443/wd/hub",
    "us-east-4": "https://ondemand.us-east-4.saucelabs.com:443/wd/hub",
    "eu-central-1": "https://ondemand.eu-central-1.saucelabs.com:443/wd/hub",
    "asia-south-2": "https://ondemand.asia-south-2.saucelabs.com:443/wd/hub",
}
ROOT = Path(__file__).resolve().parents[1]


def _valor(nombre: str, *, requerido: bool = True, default: str | None = None) -> str | None:
    valor = os.environ.get(nombre, default)
    if requerido and (not valor or valor.startswith("$(")):
        raise ValueError(
            f"Falta {nombre}. Configuralo como variable secreta de Azure Pipelines "
            "o como variable de entorno local."
        )
    return valor


def _capabilities(usuario: str, clave: str, tunel: str | None) -> dict:
    opciones = {
        "devTools": True,
        "username": usuario,
        "accessKey": clave,
        "name": os.environ.get("SAUCE_TEST_NAME", "E2E Tienda Playwright"),
        "build": os.environ.get("BUILD_BUILDNUMBER", "local"),
    }
    if tunel:
        opciones["tunnelName"] = tunel
    return {
        "platformName": os.environ.get("SAUCE_PLATFORM", "Windows 11"),
        "browserName": os.environ.get("SAUCE_BROWSER", "chrome"),
        "browserVersion": os.environ.get("SAUCE_BROWSER_VERSION", "latest"),
        "sauce:options": opciones,
    }


def _mostrar_demo() -> int:
    region = os.environ.get("SAUCE_REGION", "us-west-1")
    endpoint = ENDPOINTS.get(region)
    if endpoint is None:
        raise ValueError(f"SAUCE_REGION invalida: {region}. Usa una de: {', '.join(ENDPOINTS)}")
    ejemplo = _capabilities("__SAUCE_USERNAME__", "__SAUCE_ACCESS_KEY__", "__SAUCE_TUNNEL_NAME__")
    ejemplo["sauce:options"]["accessKey"] = "__SECRET_NO_VERSIONAR__"
    print("===== FASE 4 - Demo guiada Sauce Labs =====")
    print("No se abrira una sesion remota ni se usaran credenciales.")
    print(f"Endpoint remoto preparado : {endpoint}")
    print("BASE_URL esperada         : SAUCE_BASE_URL (URL publica) o URL a traves de Sauce Connect")
    print("Capacidades preparadas:")
    print(json.dumps(ejemplo, indent=2))
    print("Para ejecutar de verdad, define SAUCE_USERNAME, SAUCE_ACCESS_KEY y SAUCE_BASE_URL.")
    return 0


def _ejecutar() -> int:
    usuario = _valor("SAUCE_USERNAME")
    clave = _valor("SAUCE_ACCESS_KEY")
    base_url = _valor("SAUCE_BASE_URL")
    region = _valor("SAUCE_REGION", requerido=False, default="us-west-1")
    endpoint = ENDPOINTS.get(region)
    if endpoint is None:
        raise ValueError(f"SAUCE_REGION invalida: {region}. Usa una de: {', '.join(ENDPOINTS)}")
    if not str(base_url).startswith(("http://", "https://")):
        raise ValueError("SAUCE_BASE_URL debe iniciar con http:// o https://")

    capacidades = _capabilities(str(usuario), str(clave), _valor("SAUCE_TUNNEL_NAME", requerido=False))
    entorno = os.environ.copy()
    entorno["BASE_URL"] = str(base_url)
    entorno["SELENIUM_REMOTE_URL"] = endpoint
    entorno["SELENIUM_REMOTE_CAPABILITIES"] = json.dumps(capacidades)

    print("===== FASE 4 - Ejecucion remota Sauce Labs =====")
    print(f"Endpoint remoto : {endpoint}")
    print(f"Aplicacion      : {base_url}")
    print(f"Plataforma      : {capacidades['platformName']}")
    print(f"Navegador       : {capacidades['browserName']} {capacidades['browserVersion']}")
    print("Credenciales: recibidas como secretos (no se imprimen).")
    comando = [
        sys.executable,
        "-m",
        "pytest",
        "--browser",
        "chromium",
        "--headed",
        "--junitxml=resultados/sauce-junit.xml",
        "-o",
        "junit_family=xunit2",
    ]
    return subprocess.call(comando, cwd=ROOT, env=entorno)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="Valida y muestra la configuracion sin conectarse a Sauce Labs.")
    args = parser.parse_args()
    try:
        return _mostrar_demo() if args.demo else _ejecutar()
    except ValueError as error:
        print(f"[CONFIGURACION INVALIDA] {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
