# FASE 5 - Imagen reproducible de la app Tienda.
# El contexto de construccion es la raiz del repositorio porque se necesitan
# tanto app-tienda/ como datos/ para generar db.json dentro de la imagen.
FROM node:20-alpine

WORKDIR /opt/tienda

# Instalar dependencias bloqueadas antes de copiar el codigo para aprovechar cache.
COPY datos/package*.json ./datos/
RUN npm ci --prefix ./datos

COPY app-tienda/package*.json ./app-tienda/
RUN npm ci --prefix ./app-tienda --omit=dev

COPY datos ./datos
COPY app-tienda ./app-tienda

# db.json es derivado y no se copia desde la maquina anfitriona: se regenera
# dentro de la imagen con la misma semilla fija usada por el pipeline.
RUN node ./datos/generar-datos.js

WORKDIR /opt/tienda/app-tienda
ENV NODE_ENV=production
ENV PORT=3000

EXPOSE 3000

# El reto exige que /api/health sea el healthcheck del contenedor.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:3000/api/health').then(r => process.exit(r.ok ? 0 : 1)).catch(() => process.exit(1))"

CMD ["node", "servidor/server.js"]
