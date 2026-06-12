import { drizzle, type PostgresJsDatabase } from "drizzle-orm/postgres-js"
import postgres, { type Sql } from "postgres"
import * as schema from "./schema"

export type DatabaseSchema = typeof schema
export type Database = PostgresJsDatabase<DatabaseSchema>

export type CreateDbOptions = {
  databaseUrl?: string
  maxConnections?: number
}

function resolveDatabaseUrl(databaseUrl?: string): string {
  const url = databaseUrl ?? process.env.DATABASE_URL

  if (!url) {
    throw new Error("DATABASE_URL is required to initialize the database client")
  }

  return url
}

export function createPostgresClient(options: CreateDbOptions = {}): Sql {
  const maxConnections = options.maxConnections ?? Number(process.env.DB_POOL_MAX ?? 10)

  return postgres(resolveDatabaseUrl(options.databaseUrl), {
    max: Number.isFinite(maxConnections) ? maxConnections : 10,
    idle_timeout: 20,
    connect_timeout: 10,
  })
}

export function createDb(
  client: Sql = createPostgresClient(),
  dbSchema: DatabaseSchema = schema,
): Database {
  return drizzle(client, { schema: dbSchema })
}

let sharedClient: Sql | undefined
let sharedDb: Database | undefined

export function getDb(): Database {
  if (!sharedDb) {
    sharedClient = createPostgresClient()
    sharedDb = createDb(sharedClient)
  }

  return sharedDb
}

export async function closeDb(): Promise<void> {
  if (sharedClient) {
    await sharedClient.end({ timeout: 5 })
    sharedClient = undefined
    sharedDb = undefined
  }
}

export const db = getDb()
