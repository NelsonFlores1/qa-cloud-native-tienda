import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Verifier } from '@pact-foundation/pact';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const raiz = path.resolve(__dirname, '..', '..');
const appDir = path.join(raiz, 'app-tienda');
const pacto = path.join(raiz, 'pact', 'pacts', 'TiendaWeb-TiendaApi.json');
const puerto = Number(process.env.PACT_PROVIDER_PORT || 3100);
const baseUrl = `http://127.0.0.1:${puerto}`;

if (!existsSync(pacto)) {
  throw new Error('No existe el pact. Ejecuta primero: npm run test:consumer');
}
if (!existsSync(path.join(appDir, 'datos', 'db.json'))) {
  throw new Error('No existe app-tienda/datos/db.json. Ejecuta primero: npm --prefix datos run generar');
}

function esperarSalud(intentos = 30) {
  return new Promise((resolve, reject) => {
    let intento = 0;
    const timer = setInterval(async () => {
      intento += 1;
      try {
        const respuesta = await fetch(`${baseUrl}/api/health`);
        if (respuesta.ok) {
          clearInterval(timer);
          resolve();
          return;
        }
      } catch {
        // La app aun se esta iniciando.
      }
      if (intento >= intentos) {
        clearInterval(timer);
        reject(new Error(`La API no respondio en ${baseUrl}/api/health`));
      }
    }, 500);
  });
}

const servidor = spawn(process.execPath, ['servidor/server.js'], {
  cwd: appDir,
  env: { ...process.env, PORT: String(puerto) },
  stdio: 'inherit',
});

try {
  await esperarSalud();
  await new Verifier({
    provider: 'TiendaApi',
    providerBaseUrl: baseUrl,
    pactUrls: [pacto],
    stateHandlers: {
      'hay productos disponibles': () => Promise.resolve(),
    },
    logLevel: 'warn',
  }).verifyProvider();
  console.log('PACT PROVIDER VERIFIED: TiendaApi cumple GET /api/productos.');
} finally {
  servidor.kill();
}
