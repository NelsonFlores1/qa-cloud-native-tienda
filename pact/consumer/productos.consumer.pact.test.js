import assert from 'node:assert/strict';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { MatchersV3, PactV3 } from '@pact-foundation/pact';
import { obtenerProductos } from './cliente-productos.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const pactDir = path.resolve(__dirname, '..', 'pacts');
const { eachLike, integer, string, decimal } = MatchersV3;

const pacto = new PactV3({
  consumer: 'TiendaWeb',
  provider: 'TiendaApi',
  dir: pactDir,
  logLevel: 'warn',
});

pacto
  .given('hay productos disponibles')
  .uponReceiving('una consulta del catalogo')
  .withRequest({
    method: 'GET',
    path: '/api/productos',
    headers: { Accept: 'application/json' },
  })
  .willRespondWith({
    status: 200,
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
    body: eachLike({
      id: integer(1),
      nombre: string('Juego de sabanas Plus'),
      categoria: string('hogar'),
      descripcion: string('Producto de ejemplo.'),
      precio: decimal(141.99),
      stock: integer(54),
    }),
  });

await pacto.executeTest(async (mockServer) => {
  const productos = await obtenerProductos(mockServer.url);
  assert.ok(Array.isArray(productos), 'El cliente debe recibir un arreglo.');
  assert.ok(productos.length > 0, 'El catalogo pactado no puede estar vacio.');
  assert.equal(typeof productos[0].id, 'number');
  assert.equal(typeof productos[0].nombre, 'string');
  assert.equal(typeof productos[0].precio, 'number');
});

console.log(`PACT GENERADO: ${path.join(pactDir, 'TiendaWeb-TiendaApi.json')}`);
