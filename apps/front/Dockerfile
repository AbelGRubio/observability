# ──────────────────────────────────────────────
# Stage 1: Build — Instalar dependencias y compilar
# ──────────────────────────────────────────────
FROM node:20-alpine AS builder

# Instalar pnpm globalmente en esta etapa
RUN npm install -g pnpm

WORKDIR /app

# Copiar archivos de configuración de paquetes
COPY package.json pnpm-lock.yaml* ./

# Instalar dependencias bloqueando las versiones exactas
RUN pnpm install --frozen-lockfile

# Copiar el resto del código del frontend
COPY . .

# Desactivar la telemetría de Next durante el build (opcional, acelera un poco)
ENV NEXT_TELEMETRY_DISABLED=1

# Ejecutar el build de producción
RUN pnpm run build

# ──────────────────────────────────────────────
# Stage 2: Run — Imagen ligera de producción con Node
# ──────────────────────────────────────────────
FROM node:20-alpine AS run

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
# Si vas a usar AWS, asegúrate de que estas variables se inyecten en el contenedor
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Crear un usuario sin privilegios por seguridad
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copiar la carpeta .next (compilada), la carpeta public y los node_modules necesarios
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Cambiar al usuario seguro
USER nextjs

EXPOSE 3000

# Arrancar Next.js en modo producción
CMD ["node_modules/.bin/next", "start"]
