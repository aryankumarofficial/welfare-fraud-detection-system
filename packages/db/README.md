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

For the full stack (migrations run automatically before apps):

```bash
docker compose up --build
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
import { db, studentProfiles, featureSnapshots } from "@repo/db"

const profiles = await db.select().from(studentProfiles).limit(10)
```

ML inference inputs belong in `feature_snapshots`, not `student_profiles`.

See [docs/database-architecture.md](../../docs/database-architecture.md) for the full architecture guide.
