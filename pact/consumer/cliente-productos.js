/** Cliente HTTP usado por el front para consultar el catalogo. */
export async function obtenerProductos(baseUrl) {
  const respuesta = await fetch(`${baseUrl}/api/productos`, {
    headers: { Accept: 'application/json' },
  });
  if (!respuesta.ok) {
    throw new Error(`No se pudo consultar el catalogo: HTTP ${respuesta.status}`);
  }
  return respuesta.json();
}
