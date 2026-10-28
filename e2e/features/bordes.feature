# Casos de borde propuestos con IA (Claude + servidor MCP de Playwright).
# Los pasos reutilizan el vocabulario de steps_comunes.py (keywords en ingles,
# texto en espanol). Se etiquetan @ia para identificarlos en el reporte.
# Ver el prompt y el registro de la sesion en docs/prompt-ia.md.
Feature: Casos de borde de la tienda
  Como equipo de QA
  quiero cubrir comportamientos limite del catalogo y del carrito
  para detectar fallos que los caminos felices no revelan

  # Borde 1 (escenario NUEVO exigido por la fase): busqueda sin coincidencias.
  @ia @borde @catalogo
  Scenario: Buscar un producto que no existe
    Given que abro la home de la tienda
    When busco el producto "zzz-producto-inexistente"
    Then veo el mensaje de que no hay productos para el filtro

  # Borde 2 (reto extra): carrito vacio.
  @ia @borde @carrito
  Scenario: Abrir el carrito sin haber agregado productos
    Given que abro la home de la tienda
    When abro el carrito
    Then veo el mensaje de carrito vacio

  # Borde 3 (reto extra): el mismo producto dos veces suma cantidad, no duplica filas.
  @ia @borde @carrito
  Scenario: Agregar el mismo producto dos veces
    Given que abro la home de la tienda
    When agrego el producto 1 al carrito
    And agrego el producto 1 al carrito
    And abro el carrito
    Then el contador del carrito muestra 2
    And el carrito lista 1 producto distinto
