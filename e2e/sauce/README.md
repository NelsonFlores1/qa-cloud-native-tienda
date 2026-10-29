# Fase 4 - Sauce Labs en modo demo guiada

Esta carpeta prepara el framework para ejecutar los mismos escenarios de `e2e/features/` en un navegador remoto de Sauce Labs. No contiene credenciales, no inicia una cuenta ni afirma que haya ocurrido una ejecucion remota.

## Configuracion implementada

- `tools/ejecutar_sauce.py` construye las capacidades remotas desde variables de entorno y llama a la misma suite `pytest`.
- `sauce-capabilities.example.json` muestra la matriz inicial: Chrome latest sobre Windows 11.
- La integracion usa Selenium Grid y CDP, que es el mecanismo documentado por Sauce Labs para Playwright en Python.
- El stage `CloudE2E` del pipeline solo se ejecuta cuando el parametro `runSauce` se marca como `true`.

## Evidencia de la demo guiada

Desde `e2e/`, ejecutar:

```powershell
.\.venv\Scripts\python.exe tools\ejecutar_sauce.py --demo
```

El comando imprime el endpoint, la URL objetivo esperada y las capacidades sin revelar secretos ni crear una sesion remota. Tomar una captura de esa consola y guardarla en `docs/evidencias/fase4-configuracion-sauce.png`.

Tambien tomar una captura del archivo `sauce-capabilities.example.json` o del stage `CloudE2E` en Azure Pipelines. Esa evidencia demuestra la configuracion y el codigo listos para conectarse, que es la alternativa elegida cuando no hay una cuenta de Sauce Labs.

## Activacion futura con cuenta real

1. Crear en Azure Pipelines las variables secretas `SAUCE_USERNAME` y `SAUCE_ACCESS_KEY`.
2. Crear `SAUCE_BASE_URL` con una URL publica de la aplicacion. Si la aplicacion solo existe en una red privada o en `localhost`, iniciar Sauce Connect y definir tambien `SAUCE_TUNNEL_NAME`.
3. Opcionalmente cambiar `SAUCE_REGION`, `SAUCE_PLATFORM`, `SAUCE_BROWSER` y `SAUCE_BROWSER_VERSION`. El valor por defecto usa US West, Windows 11 y Chrome latest.
4. En **Run pipeline**, marcar `Ejecutar E2E en Sauce Labs` como `true`.
5. El stage `CloudE2E` ejecuta `python tools/ejecutar_sauce.py`, publica `sauce-junit.xml` y bloquea `Deploy` si la ejecucion remota falla.

## Variables que no se versionan

| Variable | Tipo | Ejemplo o uso |
|---|---|---|
| `SAUCE_USERNAME` | Secreta | Usuario de Sauce Labs |
| `SAUCE_ACCESS_KEY` | Secreta | Access key de Sauce Labs |
| `SAUCE_BASE_URL` | Variable | `https://mi-app.ejemplo.com` |
| `SAUCE_TUNNEL_NAME` | Variable opcional | Nombre del tunel Sauce Connect |
| `SAUCE_REGION` | Variable opcional | `us-west-1` |
| `SAUCE_PLATFORM` | Variable opcional | `Windows 11` |
| `SAUCE_BROWSER` | Variable opcional | `chrome` o `MicrosoftEdge` |
| `SAUCE_BROWSER_VERSION` | Variable opcional | `latest` |

Referencias: [Selenium Grid para Playwright](https://docs.saucelabs.com/web-apps/automated-testing/playwright/selenium-grid/) y [endpoints de Sauce Labs](https://docs.saucelabs.com/basics/data-center-endpoints/).
