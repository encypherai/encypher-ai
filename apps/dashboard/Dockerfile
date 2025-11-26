# Dashboard Dockerfile - includes design-system as local dependency
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copy package files for both dashboard and design-system
COPY apps/dashboard/package.json apps/dashboard/package-lock.json* ./
COPY packages/design-system/package.json ../packages/design-system/

# Update the local dependency path for Docker context
RUN sed -i 's|file:../../packages/design-system|file:../packages/design-system|g' package.json

# Install dependencies
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app

# Copy design-system first
COPY packages/design-system ../packages/design-system

# Copy dashboard source
COPY apps/dashboard ./

# Copy node_modules from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Set environment variables for build
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# Build the application
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy built assets
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
