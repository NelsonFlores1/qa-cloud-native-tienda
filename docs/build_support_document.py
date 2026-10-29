from pathlib import Path
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


ROOT = Path(r"C:\Users\Nelson\Documents\GitHub\qa-cloud-native-tienda")
OUT = ROOT / "docs" / "documento-soporte-reto-modulo5-fases4y5.docx"

NAVY = "17365D"
BLUE = "D9EAF7"
PALE = "F4F7FA"
GREEN = "E2F0D9"
AMBER = "FFF2CC"
RED = "FCE4D6"
GRID = "D9D9D9"


def shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_border(cell, color=GRID, size="6"):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = "w:" + edge
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:color"), color)


def set_cell_padding(cell, top=100, start=120, bottom=100, end=120):
    tc_pr = cell._tc.get_or_add_tcPr()
    mar = tc_pr.first_child_found_in("w:tcMar")
    if mar is None:
        mar = OxmlElement("w:tcMar")
        tc_pr.append(mar)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        tag = qn("w:" + side)
        element = mar.find(tag)
        if element is None:
            element = OxmlElement("w:" + side)
            mar.append(element)
        element.set(qn("w:w"), str(value))
        element.set(qn("w:type"), "dxa")


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_col_width(cell, cm):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_w = tc_pr.find(qn("w:tcW"))
    if tc_w is None:
        tc_w = OxmlElement("w:tcW")
        tc_pr.append(tc_w)
    tc_w.set(qn("w:w"), str(int(cm * 567)))
    tc_w.set(qn("w:type"), "dxa")


def set_font(run, size=None, bold=None, color=None, italic=None):
    run.font.name = "Aptos"
    run._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
    run._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color:
        run.font.color.rgb = RGBColor.from_string(color)


def remove_paragraph_borders(paragraph):
    """Override the built-in Word Title rule with explicit nil borders."""
    p_pr = paragraph._p.get_or_add_pPr()
    existing = p_pr.find(qn("w:pBdr"))
    if existing is not None:
        p_pr.remove(existing)
    borders = OxmlElement("w:pBdr")
    for edge in ("top", "left", "bottom", "right", "between", "bar"):
        border = OxmlElement("w:" + edge)
        border.set(qn("w:val"), "nil")
        borders.append(border)
    p_pr.append(borders)


def style_text(paragraph, size=10.5, color="000000", bold=False, alignment=None, space_after=6):
    if alignment is not None:
        paragraph.alignment = alignment
    paragraph.paragraph_format.space_after = Pt(space_after)
    paragraph.paragraph_format.line_spacing = 1.13
    for run in paragraph.runs:
        set_font(run, size=size, color=color, bold=bold)


def add_paragraph(doc, text="", *, bold_lead=None, keep=False):
    p = doc.add_paragraph()
    if keep:
        p.paragraph_format.keep_with_next = True
    if bold_lead and text.startswith(bold_lead):
        r = p.add_run(bold_lead)
        set_font(r, size=10.5, bold=True)
        r = p.add_run(text[len(bold_lead):])
        set_font(r, size=10.5)
    else:
        r = p.add_run(text)
        set_font(r, size=10.5)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.13
    return p


def add_bullet(doc, text, level=0):
    p = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
    r = p.add_run(text)
    set_font(r, size=10.3)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.1
    return p


def heading(doc, text, level=1):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.paragraph_format.space_before = Pt(14 if level == 1 else 9)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    set_font(r, size=15 if level == 1 else 12, bold=True, color="000000")
    return p


def add_table(doc, headers, rows, widths, status_col=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.autofit = False
    table.style = "Table Grid"
    header = table.rows[0]
    set_repeat_table_header(header)
    for i, label in enumerate(headers):
        cell = header.cells[i]
        cell.text = label
        set_col_width(cell, widths[i])
        shade(cell, NAVY)
        set_cell_border(cell)
        set_cell_padding(cell)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            set_font(run, size=9.5, bold=True, color="FFFFFF")
    for idx, row_values in enumerate(rows):
        row = table.add_row()
        for i, value in enumerate(row_values):
            cell = row.cells[i]
            cell.text = str(value)
            set_col_width(cell, widths[i])
            shade(cell, PALE if idx % 2 else "FFFFFF")
            if status_col is not None and i == status_col:
                lower = str(value).lower()
                if "verificado" in lower or "listo" in lower:
                    shade(cell, GREEN)
                elif "pendiente" in lower or "requiere" in lower:
                    shade(cell, AMBER)
                elif "no" in lower:
                    shade(cell, RED)
            set_cell_border(cell)
            set_cell_padding(cell)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.05
            if i == status_col:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                set_font(run, size=9.1, bold=(i == status_col))
    doc.add_paragraph().paragraph_format.space_after = Pt(3)
    return table


doc = Document()
section = doc.sections[0]
section.top_margin = Cm(1.8)
section.bottom_margin = Cm(1.7)
section.left_margin = Cm(2.0)
section.right_margin = Cm(2.0)

styles = doc.styles
styles["Normal"].font.name = "Aptos"
styles["Normal"]._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
styles["Normal"]._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
styles["Normal"].font.size = Pt(10.5)

footer = section.footer
footer_p = footer.paragraphs[0]
footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
footer_p.text = "QA Cloud Native Tienda  |  Documento de soporte  |  28 de octubre de 2026"
style_text(footer_p, size=8.5, color="666666", space_after=0)

# Portada
title = doc.add_paragraph(style="Title")
remove_paragraph_borders(title)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
title.paragraph_format.space_before = Pt(62)
title.paragraph_format.space_after = Pt(12)
r = title.add_run("Documento de soporte Reto practico Modulo 5")
set_font(r, size=25, bold=True, color="000000")

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
subtitle.paragraph_format.space_after = Pt(28)
r = subtitle.add_run("QA Cloud Native Automatizacion Inteligente con IA Generativa")
set_font(r, size=14, color=NAVY)

meta = [
    "Proyecto: QA Cloud Native Tienda",
    "Repositorio: https://github.com/NelsonFlores1/qa-cloud-native-tienda",
    "Estudiante: Nelson Flores",
    "Fecha de elaboracion: 28 de octubre de 2026",
]
for line in meta:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(line)
    set_font(r, size=10.5, color="333333")
    p.paragraph_format.space_after = Pt(5)

doc.add_paragraph().paragraph_format.space_after = Pt(42)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Conclusion de la revision")
set_font(r, size=12, bold=True, color="000000")
p.paragraph_format.space_after = Pt(8)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.left_indent = Cm(1.0)
p.paragraph_format.right_indent = Cm(1.0)
r = p.add_run(
    "Las fases 1, 2 y 3 estan implementadas y se validaron localmente. "
    "Las integraciones y evidencias que requieren acceso a Azure DevOps, GitHub, Sauce Labs y Azure "
    "se indican como pendientes del estudiante para completar la entrega."
)
set_font(r, size=11, color="333333")
p.paragraph_format.line_spacing = 1.2

doc.add_page_break()

heading(doc, "Alcance y estado general")
add_paragraph(doc, "Este documento explica las decisiones tecnicas, las validaciones locales y los entregables pendientes del reto practico. El proyecto toma como base la app Tienda y los ejemplos de las sesiones 1, 3 y 4 del repositorio de clase. La revision se realizo sobre el repositorio local y no sustituye las evidencias capturadas en servicios externos.")

add_table(
    doc,
    ["Fase", "Resultado en el repositorio", "Estado"],
    [
        ["1 Datos de prueba", "Faker con semilla fija, 24 productos, cuatro categorias y anonimizacion del dump ficticio.", "Verificado"],
        ["2 Pipeline y gates", "YAML con Build, SmokeTests, LoadTest, E2E y Deploy simulado; smoke y carga ejecutados en local.", "Verificado"],
        ["3 E2E con IA", "BDD, Screenplay, Playwright, siete escenarios y preparacion para Azure Test Plans.", "Verificado"],
        ["4 Ejecucion en la nube", "No hay configuracion ni evidencia de Sauce Labs u otro proveedor remoto.", "Pendiente"],
        ["5 Contenedores y contrato", "Dockerfile, healthcheck, contrato Pact y stages de contenedor/ACR preparados.", "Verificado local"],
        ["6 Metricas y estrategia", "No existe aun el cuadro DORA, la piramide ni la matriz de riesgos.", "Pendiente"],
    ],
    [3.0, 10.7, 3.0],
    status_col=2,
)

heading(doc, "Estructura del repositorio", 2)
add_paragraph(doc, "La estructura actual separa la aplicacion bajo prueba, los datos, los tests de pipeline y el framework E2E. Esta separacion permite preparar el estado de la app y ejecutar cada nivel de prueba de manera independiente.")
add_bullet(doc, "app-tienda contiene el front estatico, la API Express y el endpoint de salud /api/health.")
add_bullet(doc, "datos contiene el generador con Faker, el dump ficticio, la anonimizacion y la comprobacion de reproducibilidad.")
add_bullet(doc, "pipeline contiene azure-pipelines.yml, el smoke test, la prueba de carga y la plantilla para arrancar la app en cada stage.")
add_bullet(doc, "e2e contiene features Gherkin, steps pytest-bdd, el patron Screenplay, evidencia Allure y la publicacion preparada para Azure Test Plans.")

heading(doc, "Fase 1 Datos de prueba realistas")
add_paragraph(doc, "La fuente de verdad del catalogo es datos/generar-datos.js. El script fija la semilla de Faker en 2025, crea 24 productos y los distribuye en las categorias hogar, tecnologia, ropa y juguetes. Cada categoria define sus propios articulos, rangos de precio, rangos de stock y descripciones para mantener coherencia entre los campos.")

heading(doc, "Validacion realizada", 2)
add_table(
    doc,
    ["Comprobacion", "Resultado observado"],
    [
        ["Reproducibilidad", "Dos ejecuciones produjeron el mismo SHA 256: 372d4a1df0e461803fa52ae72298d16c43222ec4b4d2239cb89d501a6401f2a1."],
        ["Catalogo", "24 productos: hogar 6, tecnologia 6, ropa 6 y juguetes 6."],
        ["Anonimizacion", "10 clientes anonimizados. Se sustituyen nombre y correo, se elimina el telefono y se verifica que no persistan datos personales originales."],
        ["Datos derivados", "app-tienda/datos/db.json se regenera desde el script y se excluye de Git para evitar inconsistencias y ruido en los cambios."],
    ],
    [4.0, 12.7],
)

heading(doc, "Entregable y evidencia pendiente", 2)
add_paragraph(doc, "El codigo requerido y la explicacion sobre db.json ya estan presentes. Para la entrega final, incluir una captura de la consola con npm run verificar y otra con npm run anonimizar si se solicita evidencia visual de esta fase.")

heading(doc, "Fase 2 Pipeline CI CD con quality gates")
add_paragraph(doc, "El archivo pipeline/azure-pipelines.yml define cinco stages. Build instala dependencias y genera los datos. SmokeTests valida que la aplicacion este disponible. LoadTest evalua el SLA. E2E ejecuta los escenarios BDD y publica sus resultados. Deploy es simulado y solo se ejecuta si todos los gates anteriores terminan correctamente.")

add_table(
    doc,
    ["Gate", "Que valida", "Comportamiento ante fallo"],
    [
        ["Gate 1 SmokeTests", "Salud, catalogo, producto, 404, filtro, front y creacion de pedido.", "El script termina con codigo 1 y bloquea los stages siguientes."],
        ["Gate 2 LoadTest", "p95 menor que 800 ms y tasa de error menor que 1 por ciento.", "El script termina con codigo 1 si el SLA no se cumple."],
        ["Gate 3 E2E", "Escenarios Gherkin ejecutados por pytest y Playwright.", "pytest devuelve un codigo distinto de cero cuando un escenario falla."],
    ],
    [3.2, 6.5, 7.0],
)

heading(doc, "Evidencia local obtenida", 2)
add_bullet(doc, "Smoke test: 7 de 7 comprobaciones aprobadas.")
add_bullet(doc, "Carga con SLA normal: 39 501 peticiones, p95 de 2.2 ms y 0.00 por ciento de errores. El gate aprobó.")
add_bullet(doc, "Carga con SLA forzado a 1 ms: 41 363 peticiones, p95 de 1.9 ms y 0.00 por ciento de errores. El gate falló por p95, como se espera.")

heading(doc, "Acciones necesarias del estudiante", 2)
add_bullet(doc, "Conectar el repositorio de GitHub a Azure Pipelines y seleccionar pipeline/azure-pipelines.yml como archivo de configuracion.")
add_bullet(doc, "Ejecutar una corrida con el SLA por defecto y guardar una captura donde LoadTest aparezca en verde.")
add_bullet(doc, "Ejecutar otra corrida con el parametro slaP95Ms igual a 1 y guardar una captura donde LoadTest aparezca en rojo y los stages posteriores queden omitidos.")
add_bullet(doc, "Insertar ambas capturas en la seccion de evidencias del documento antes de una entrega formal.")

heading(doc, "Fase 3 Del caso manual al automatizado con IA")
add_paragraph(doc, "La automatizacion E2E conserva los tres flujos de negocio del reto: catalogo, carrito y pedidos. Los features usan keywords Gherkin en ingles y pasos en espanol. Los steps delegan las acciones y consultas en tareas y preguntas del patron Screenplay, por lo que los selectores y la logica de navegacion quedan centralizados.")

add_table(
    doc,
    ["Cobertura", "Escenarios", "Resultado local"],
    [
        ["Casos principales", "Filtrar por Hogar, agregar un producto, agregar dos productos y confirmar pedido.", "4 aprobados"],
        ["Casos de borde propuestos", "Busqueda sin resultados, carrito vacio y agregar el mismo producto dos veces.", "3 aprobados"],
        ["Total", "Suite pytest con Playwright y Chromium.", "7 aprobados"],
    ],
    [4.0, 8.8, 3.9],
)

heading(doc, "Integracion con Azure Test Plans", 2)
add_paragraph(doc, "Los documentos de la carpeta e2e/docs describen los tres casos manuales y el proceso para publicar resultados. Los tags @TC19, @TC20 y @TC21 se transforman en la propiedad test_case_id del JUnit. El script tools/publicar_test_plan.py esta preparado para actualizar los Test Points mediante la API de Azure DevOps cuando se proporcionen los datos reales del plan, suite y PAT.")

heading(doc, "Acciones necesarias del estudiante", 2)
add_bullet(doc, "Crear los tres Test Cases en Azure Test Plans y reemplazar los tags de ejemplo por los IDs reales.")
add_bullet(doc, "Completar TEST_PLAN_ID y TEST_SUITE_ID en el pipeline y crear la variable secreta AZURE_DEVOPS_PAT con permiso Test Management Read and write.")
add_bullet(doc, "Ejecutar el stage E2E en Azure y capturar los resultados publicados en la pestana Tests y en la pestana Execute del plan.")
add_bullet(doc, "Usar Claude Desktop con el servidor MCP de Playwright para explorar la app, completar el registro de e2e/docs/prompt-ia.md y guardar una captura de la sesion. El archivo actual declara los casos de borde como borrador y no como evidencia de una sesion MCP real.")

heading(doc, "Fase 4 Ejecucion en la nube")
add_paragraph(doc, "Se eligio la modalidad de demo guiada porque no se cuenta con una cuenta de Sauce Labs. La configuracion esta preparada para ejecutar los mismos escenarios en Chrome latest sobre Windows 11 mediante Sauce Labs Selenium Grid y CDP. El ejecutor e2e/tools/ejecutar_sauce.py construye las capacidades desde variables de entorno y conserva los escenarios existentes sin modificarlos.")
add_table(
    doc,
    ["Entregable requerido", "Implementacion disponible", "Estado"],
    [
        ["Configuracion remota", "e2e/sauce/sauce-capabilities.example.json declara plataforma, navegador, build y tunel sin exponer secretos." , "Listo"],
        ["Codigo listo", "e2e/tools/ejecutar_sauce.py lee BASE_URL, credenciales y capacidades; --demo valida la configuracion sin abrir una sesion remota.", "Listo"],
        ["Pipeline", "CloudE2E ejecuta la demo por defecto. Al marcar runSauce=true, ejecuta pytest remoto, publica JUnit y bloquea Deploy ante fallo.", "Listo"],
        ["Evidencia", "Falta guardar una captura de la salida --demo y otra del stage CloudE2E en Azure Pipelines.", "Requiere captura"],
    ],
    [3.3, 10.2, 3.2],
    status_col=2,
)

heading(doc, "Acciones necesarias del estudiante", 2)
add_bullet(doc, "Ejecutar .\\.venv\\Scripts\\python.exe tools\\ejecutar_sauce.py --demo desde e2e y guardar la consola como docs/evidencias/fase4-configuracion-sauce.png.")
add_bullet(doc, "Subir los cambios a GitHub, ejecutar el pipeline con Ejecutar E2E en Sauce Labs desmarcado y capturar el stage CloudE2E en verde. Esta ejecucion valida la configuracion, pero no representa una ejecucion remota real.")
add_bullet(doc, "Para una ejecucion real futura, crear las variables secretas SAUCE_USERNAME y SAUCE_ACCESS_KEY, definir SAUCE_BASE_URL como URL publica o configurar Sauce Connect y SAUCE_TUNNEL_NAME, y ejecutar el pipeline con runSauce=true.")

heading(doc, "Fase 5 Contenedores y contract testing")
add_paragraph(doc, "La aplicacion se contenedorizo con un Dockerfile en la raiz. La imagen instala las dependencias bloqueadas, genera db.json dentro del contenedor con la semilla fija y expone el puerto 3000. El healthcheck invoca /api/health, por lo que la misma ruta valida tanto la aplicacion local como la imagen resultante.")
add_table(
    doc,
    ["Entregable", "Implementacion", "Estado"],
    [
        ["Imagen contenedorizada", "Dockerfile con Node 20 Alpine, generacion interna de datos, puerto 3000 y HEALTHCHECK sobre /api/health.", "Listo"],
        ["Contrato consumer", "TiendaWeb genera un Pact para GET /api/productos con respuesta 200, JSON y los campos del producto.", "Verificado"],
        ["Contrato provider", "TiendaApi se inicia en el puerto 3100 y Pact verifica el contrato generado contra la API real.", "Verificado"],
        ["ACR", "Stage AcrPublication preparado. La publicacion real requiere suscripcion, service connection y ACR_NAME.", "Demo guiada"],
    ],
    [3.3, 10.2, 3.2],
    status_col=2,
)

heading(doc, "Validacion realizada", 2)
add_bullet(doc, "El contrato Pact TiendaWeb - TiendaApi fue generado en pact/pacts/TiendaWeb-TiendaApi.json.")
add_bullet(doc, "La verificacion del provider termino en verde: respuesta 200, Content-Type application/json; charset=utf-8 y cuerpo compatible para GET /api/productos.")
add_bullet(doc, "Docker Desktop esta instalado en el equipo, pero su motor no estaba iniciado durante la revision. Por ello, la construccion y ejecucion local de la imagen debe evidenciarse al iniciar Docker Desktop o al ejecutar el stage Container en Azure Pipelines.")

heading(doc, "Acciones necesarias del estudiante", 2)
add_bullet(doc, "Iniciar Docker Desktop y ejecutar docker build -t tienda-qa:local ., docker run y docker inspect para capturar el estado healthy y la respuesta de /api/health.")
add_bullet(doc, "Ejecutar npm test desde pact y guardar una captura de PACT PROVIDER VERIFIED junto con el archivo TiendaWeb-TiendaApi.json.")
add_bullet(doc, "Subir los cambios y ejecutar el pipeline para capturar los stages Container y ContractTests en verde.")
add_bullet(doc, "Para publicar de verdad, crear una service connection de Azure, definir AZURE_SUBSCRIPTION y ACR_NAME, y ejecutar el pipeline con publishAcr=true. Sin una suscripcion, declarar la publicacion ACR como demo guiada.")

heading(doc, "Fase 6 Metricas y estrategia")
add_paragraph(doc, "La fase 6 exige medir el flujo y justificar la estrategia de calidad. Los valores deben ser estimados de forma razonada si no se cuenta con datos de produccion, pero deben dejar claro su fuente y periodo de referencia.")
add_table(
    doc,
    ["Entregable", "Contenido que debes completar"],
    [
        ["Metricas DORA", "Frecuencia de despliegue, lead time, tasa de fallos de cambio y MTTR. Registrar periodo, formula y fuente de cada valor."],
        ["Piramide de pruebas", "Ubicar pruebas unitarias, integracion, API, E2E, carga y contrato; justificar el nivel y el costo de cada una."],
        ["Riesgos y mitigaciones", "Describir al menos tres riesgos reales: datos inestables, dependencia de servicios externos, selectores fragiles, rendimiento o secretos. Asociar una mitigacion verificable a cada riesgo."],
    ],
    [4.4, 12.3],
)

heading(doc, "Checklist de cierre")
add_paragraph(doc, "Antes de entregar, revisar que el repositorio y este documento cuenten con todos los artefactos que pide el reto. No deben presentarse como ejecuciones reales las actividades que solo estan configuradas o documentadas.")
add_table(
    doc,
    ["Elemento", "Situacion actual", "Siguiente accion"],
    [
        ["Codigo fases 1 a 3", "Implementado y validado localmente.", "Conservar README y comandos de ejecucion actualizados."],
        ["Capturas Azure Pipelines", "No estan en docs/evidencias.", "Agregar corrida verde y roja del gate de carga."],
        ["Azure Test Plans", "Documentacion y script listos; IDs y PAT vacios.", "Crear casos, configurar variables y capturar la publicacion."],
        ["Uso real de MCP", "Prompt y borrador existentes; registro incompleto.", "Ejecutar sesion, completar tabla de registro y adjuntar captura."],
        ["Fase 4", "Demo guiada implementada; faltan las dos capturas de configuracion.", "Ejecutar la demo y capturar CloudE2E en Azure."],
        ["Fase 5", "Dockerfile y Pact implementados; falta evidencia de imagen y ACR si se requiere ejecucion real.", "Ejecutar Docker/Pipeline y conservar capturas."],
        ["Fase 6", "Pendiente.", "Implementar los artefactos y registrar evidencia honesta."],
    ],
    [4.1, 6.1, 6.5],
)

heading(doc, "Fuentes y comandos de validacion", 2)
add_bullet(doc, "Enunciado: Reto practico 5 PDF proporcionado para esta practica.")
add_bullet(doc, "Material de clase: https://github.com/oach82/Diplomado-Modulo5 y el archivo Diplomado Modulo5 master ZIP proporcionado.")
add_bullet(doc, "Repositorio revisado: https://github.com/NelsonFlores1/qa-cloud-native-tienda.")
add_bullet(doc, "Comandos ejecutados: npm run verificar, npm run anonimizar, npm run generar, node tests/smoke-api.js, node tests/carga-simple.js y pytest con JUnit.")

doc.core_properties.title = "Documento de soporte Reto practico Modulo 5"
doc.core_properties.author = "Nelson Flores"
doc.core_properties.subject = "QA Cloud Native Tienda"
doc.core_properties.comments = "Documento de soporte con evidencias locales y pendientes de integraciones externas."
doc.save(OUT)
print(OUT)
