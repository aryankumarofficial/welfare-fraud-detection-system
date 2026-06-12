import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"
import { migrate } from "drizzle-orm/postgres-js/migrator"
import { closeDb, createDb, createPostgresClient } from "./client"

const migrationsFolder = join(dirname(fileURLToPath(import.meta.url)), "migrations")

async function runMigrations(): Promise<void> {
  const client = createPostgresClient({ maxConnections: 1 })
  const database = createDb(client)

  try {
    await migrate(database, { migrationsFolder })
    console.log("Database migrations applied successfully.")
  } finally {
    await closeDb()
    await client.end({ timeout: 5 })
  }
}

runMigrations().catch((error: unknown) => {
  console.error("Database migration failed:", error)
  process.exit(1)
})
