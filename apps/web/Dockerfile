# =========================
# Builder
# =========================
FROM node:22-bullseye-slim AS builder

WORKDIR /app

# System dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    python3 \
    python3-dev \
    python-is-python3 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Enable pnpm
RUN corepack enable \
    && corepack prepare pnpm@11.8.0 --activate

# Copy workspace manifests first (better cache)
COPY package.json ./
COPY pnpm-workspace.yaml ./
COPY bun.lock* ./
COPY tsconfig.json ./

# Copy source
COPY apps ./apps
COPY packages ./packages
COPY services ./services

# Install dependencies
RUN pnpm install --no-frozen-lockfile

# Build web app
RUN pnpm --filter web build

# =========================
# Runtime
# =========================
FROM node:22-bullseye-slim AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

RUN corepack enable \
    && corepack prepare pnpm@11.8.0 --activate

# Copy build output
COPY --from=builder /app/apps/web/.next ./.next
COPY --from=builder /app/apps/web/public ./public
COPY --from=builder /app/apps/web/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules

EXPOSE 3000

CMD ["pnpm", "start"]