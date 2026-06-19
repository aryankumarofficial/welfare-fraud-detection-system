FROM oven/bun:1

WORKDIR /app

# Copy repository into image (root .dockerignore prevents copying node_modules)
COPY . .

# Install dependencies for the workspace
RUN bun install

# Build the Next.js app from the workspace package
WORKDIR /app/apps/web
# Use `bun x` to invoke the Next binary directly (ensures workspace bin resolution)
RUN bun x next build

EXPOSE 3000

CMD ["bun","x","next","start","-p","3000"]
