/**
 * RETO EXTRA (Fase 1) - Anonimizacion de un "dump real" ficticio.
 *
 * Parte de datos/dump-real-ficticio.json (simula una exportacion con datos
 * personales) y devuelve una version SIN datos personales:
 *   - nombre   -> "Cliente <hash>"          (pseudonimo estable)
 *   - correo   -> "cliente-<hash>@anonimo.test"
 *   - telefono -> se elimina (la tienda no lo necesita)
 *   - ciudad   -> se conserva (dato agregado, no identifica a la persona)
 *
 * El hash es SHA-256 con una sal fija: la misma persona siempre produce el mismo
 * pseudonimo (los datos siguen siendo reproducibles y se pueden cruzar entre
 * tablas), pero no se puede volver al dato original.
 *
 * Uso suelto:  node anonimizar.js   (imprime el antes/despues)
 */
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const SAL = 'tienda-qa-modulo5';

function hash(texto, largo) {
  return crypto
    .createHash('sha256')
    .update(`${SAL}|${String(texto).trim().toLowerCase()}`)
    .digest('hex')
    .slice(0, largo);
}

export function anonimizarCliente(c) {
  return {
    id: c.id,
    nombre: `Cliente ${hash(c.nombre, 6)}`,
    correo: `cliente-${hash(c.correo, 10)}@anonimo.test`,
    ciudad: c.ciudad,
  };
}

export function anonimizarClientes(clientes) {
  return clientes.map(anonimizarCliente);
}

/** Falla si algun dato personal original sigue presente en la salida. */
export function verificarSinDatosPersonales(salida, originales) {
  const texto = JSON.stringify(salida).toLowerCase();
  for (const o of originales) {
    const pistas = [o.nombre, o.correo, o.telefono, o.correo.split('@')[0]];
    for (const pista of pistas) {
      if (pista && texto.includes(String(pista).toLowerCase())) {
        throw new Error(`Anonimizacion incompleta: aparece "${pista}" en la salida`);
      }
    }
  }
}

export function cargarDump() {
  const dir = path.dirname(fileURLToPath(import.meta.url));
  return JSON.parse(fs.readFileSync(path.join(dir, 'dump-real-ficticio.json'), 'utf-8'));
}

// Ejecucion directa: muestra el antes y el despues
if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  const { clientes } = cargarDump();
  const anon = anonimizarClientes(clientes);
  verificarSinDatosPersonales(anon, clientes);
  console.log('===== Anonimizacion del dump ficticio =====');
  clientes.slice(0, 3).forEach((c, i) => {
    console.log(`ANTES  : ${c.nombre} <${c.correo}> ${c.telefono}`);
    console.log(`DESPUES: ${anon[i].nombre} <${anon[i].correo}>`);
  });
  console.log(`${anon.length} clientes anonimizados; verificacion de datos personales: OK`);
}
