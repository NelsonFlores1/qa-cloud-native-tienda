/**
 * Comprueba que los datos son reproducibles: genera el catalogo DOS veces
 * (en archivos temporales) y compara el hash SHA-256 de ambos resultados.
 *
 *   npm run verificar
 *
 * Con la semilla fija y la version exacta de Faker, los hashes deben coincidir
 * en cualquier maquina (se puede comparar tambien entre tu PC y el agente de Azure).
 */
import { execFileSync } from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const script = path.join(dir, 'generar-datos.js');

function generarYHashear(n) {
  const tmp = path.join(os.tmpdir(), `db-verificacion-${process.pid}-${n}.json`);
  execFileSync(process.execPath, [script], { env: { ...process.env, DB_SALIDA: tmp }, stdio: 'ignore' });
  const hash = crypto.createHash('sha256').update(fs.readFileSync(tmp)).digest('hex');
  fs.rmSync(tmp, { force: true });
  return hash;
}

const h1 = generarYHashear(1);
const h2 = generarYHashear(2);
console.log('Corrida 1 SHA-256:', h1);
console.log('Corrida 2 SHA-256:', h2);
if (h1 !== h2) {
  console.error('FALLO: los datos NO son reproducibles.');
  process.exit(1);
}
console.log('OK: datos reproducibles (mismo hash en ambas corridas).');
