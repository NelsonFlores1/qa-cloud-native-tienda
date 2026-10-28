/**
 * FASE 1 - Datos de prueba realistas: catalogo de la tienda con Faker + semilla fija.
 *
 * Produce  app-tienda/datos/db.json  (la ruta que lee el servidor) con:
 *   { productos: [...], pedidos: [], clientes: [...] }
 *
 *   - productos: 24, en 4 categorias (hogar, tecnologia, ropa, juguetes: las mismas
 *     que ofrece el filtro del front). Los campos son COHERENTES con la categoria:
 *     nombre, descripcion, rango de precio y rango de stock salen de la misma
 *     configuracion, asi no aparece una "Lámpara" de $1.100 ni un "Monitor" de $12.
 *   - clientes: viene del reto extra. Se parte de un dump "real" ficticio
 *     (dump-real-ficticio.json) y se ANONIMIZA (nombres y correos) antes de usarlo.
 *   - pedidos: arranca vacio; los crean las pruebas.
 *
 * Semilla FIJA (faker.seed) + version exacta de Faker (package.json) -> mismo db.json
 * en cualquier maquina y en cada corrida. Se comprueba con: npm run verificar
 *
 * db.json NO se versiona (esta en .gitignore): es un artefacto derivado que el
 * pipeline regenera en cada corrida a partir de este script y la semilla.
 *
 * Ejecutar (desde la raiz del repo):
 *   cd datos && npm install && node generar-datos.js
 */
import { faker } from '@faker-js/faker';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { anonimizarClientes, cargarDump, verificarSinDatosPersonales } from './anonimizar.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
// DB_SALIDA permite redirigir la salida (lo usa verificar-reproducibilidad.js)
const rutaSalida = process.env.DB_SALIDA || path.join(__dirname, '..', 'app-tienda', 'datos', 'db.json');

const SEMILLA = 2025;
faker.seed(SEMILLA);

const CANT_PRODUCTOS = 24; // requisito del reto: 20+

// Cada categoria define sus propios nombres, textos, precios y stock.
const CATALOGO = {
  hogar: {
    articulos: ['Lámpara', 'Juego de sábanas', 'Set de ollas', 'Cortinas', 'Alfombra', 'Licuadora', 'Almohada', 'Organizador'],
    adjetivos: ['Elegante', 'Resistente', 'Versátil', 'Premium', 'Esencial', 'Plus'],
    frases: ['Ideal para renovar cualquier ambiente de la casa.', 'Pensado para el uso diario en el hogar.', 'Fácil de limpiar y de larga duración.'],
    precio: { min: 15, max: 300 },
    stock: { min: 5, max: 80 },
  },
  tecnologia: {
    articulos: ['Auriculares', 'Teclado', 'Mouse', 'Monitor', 'Parlante', 'Cargador', 'Webcam', 'Tablet'],
    adjetivos: ['Portátil', 'Smart', 'Pro', 'Ultra', 'Plus', 'Premium'],
    frases: ['Compatible con la mayoría de los dispositivos.', 'Ideal para trabajar, estudiar o jugar.', 'Incluye garantía de fábrica.'],
    precio: { min: 25, max: 1200 },
    stock: { min: 1, max: 40 },
  },
  ropa: {
    articulos: ['Camiseta', 'Chaqueta', 'Jeans', 'Zapatillas', 'Sudadera', 'Gorra', 'Bufanda', 'Camisa'],
    adjetivos: ['Casual', 'Elegante', 'Premium', 'Esencial', 'Plus', 'Versátil'],
    frases: ['Tela comoda y de buena calidad.', 'Disponible en varias tallas.', 'Perfecto para el día a día.'],
    precio: { min: 10, max: 180 },
    stock: { min: 10, max: 120 },
  },
  juguetes: {
    articulos: ['Rompecabezas', 'Bloques de construcción', 'Muñeco articulado', 'Carro a control remoto', 'Peluche', 'Juego de mesa', 'Pelota', 'Set de pintura'],
    adjetivos: ['Familiar', 'Infantil', 'Premium', 'Plus', 'Esencial', 'Resistente'],
    frases: ['Estimula la imaginación y la creatividad.', 'Recomendado para jugar en familia.', 'Fabricado con materiales seguros.'],
    precio: { min: 8, max: 150 },
    stock: { min: 5, max: 60 },
  },
};
const CATEGORIAS = Object.keys(CATALOGO);

// ── Productos ────────────────────────────────────────────────
const nombresUsados = new Set();

function crearProducto(id) {
  // Las categorias se alternan (1=hogar, 2=tecnologia, 3=ropa, 4=juguetes, 5=hogar...)
  const categoria = CATEGORIAS[(id - 1) % CATEGORIAS.length];
  const cfg = CATALOGO[categoria];

  let nombre;
  do {
    nombre = `${faker.helpers.arrayElement(cfg.articulos)} ${faker.helpers.arrayElement(cfg.adjetivos)}`;
  } while (nombresUsados.has(nombre));
  nombresUsados.add(nombre);

  return {
    id,
    nombre,
    categoria,
    descripcion: `${nombre}. ${faker.helpers.arrayElement(cfg.frases)}`,
    precio: Number(faker.commerce.price({ min: cfg.precio.min, max: cfg.precio.max, dec: 2 })),
    stock: faker.number.int(cfg.stock),
  };
}

const productos = Array.from({ length: CANT_PRODUCTOS }, (_, i) => crearProducto(i + 1));

// ── Clientes: dump ficticio -> anonimizacion (reto extra) ────
const { clientes: clientesOriginales } = cargarDump();
const clientes = anonimizarClientes(clientesOriginales);
verificarSinDatosPersonales(clientes, clientesOriginales); // corta si se filtra algun dato

// ── Escribir db.json ─────────────────────────────────────────
const db = { productos, pedidos: [], clientes };
fs.mkdirSync(path.dirname(rutaSalida), { recursive: true });
fs.writeFileSync(rutaSalida, JSON.stringify(db, null, 2) + '\n', 'utf-8');

// ── Resumen ──────────────────────────────────────────────────
const porCategoria = CATEGORIAS.map((c) => `${c}: ${productos.filter((p) => p.categoria === c).length}`).join(' | ');
console.log('===== FASE 1: generar datos con Faker =====');
console.log(`Semilla fija : ${SEMILLA}`);
console.log(`Productos    : ${productos.length}  (${porCategoria})`);
console.log(`Clientes     : ${clientes.length} anonimizados (dump ficticio, verificacion de datos personales OK)`);
console.log(`Ejemplo      : ${productos[0].nombre} (${productos[0].categoria}) $${productos[0].precio}, stock ${productos[0].stock}`);
console.log(`Escrito en   : ${path.relative(process.cwd(), rutaSalida) || rutaSalida}`);
console.log('============================================');
