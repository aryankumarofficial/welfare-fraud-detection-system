# @repo/db

Shared PostgreSQL schema, migrations, and TypeScript client for the Welfare Fraud Detection System.

## Quick Start

```bash
# From repository root
cp .env.example .env
docker compose up -d postgres
bun install
bun run db:migrate
```

## Scripts

| Command | Description |
| --- | --- |
| `bun run db:generate` | Generate SQL migration from schema changes |
| `bun run db:migrate` | Apply pending migrations |
| `bun run db:push` | Push schema directly (local prototyping only) |
| `bun run db:studio` | Open Drizzle Studio |
| `bun run db:check` | Validate migration files |

## Usage

```ts
import { db, studentProfiles, predictionRecords } from "@repo/db"

const profiles = await db.select().from(studentProfiles).limit(10)
```

For long-lived servers, prefer `getDb()` and `closeDb()` from `@repo/db/client` when you need explicit lifecycle control.

See [docs/database-architecture.md](../../docs/database-architecture.md) for the full architecture guide.
