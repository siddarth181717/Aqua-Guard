# Production Multi-stage Dockerfile for AquaGuard Next.js / React Frontend
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code and build application
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production
RUN npm run build

# Production Runner Stage
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Copy built application assets
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./ 2>/dev/null || true
COPY --from=builder /app/.next/static ./.next/static 2>/dev/null || true
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/src ./src

EXPOSE 3000

CMD ["npm", "run", "start"]
