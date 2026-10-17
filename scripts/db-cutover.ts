import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "../src/db/schema";

const [direction = "", flag] = process.argv.slice(2);
if (!["up", "down"].includes(direction)) {
  console.error("usage: bun scripts/db-cutover.ts <up|down> [--dry-run]");
  process.exit(1);
}
const dryRun = flag === "--dry-run";
const file =
  direction === "up" ? "0000_better_auth_cutover.sql" : "0000_better_auth_cutover.down.sql";
const migration = await Bun.file(new URL(`../drizzle/${file}`, import.meta.url)).text();

class DryRunRollback extends Error {}

const sql = postgres(process.env.DATABASE_URL!, { max: 1, prepare: false });
try {
  await sql.begin(async (tx) => {
    await tx.unsafe(migration);
    if (direction === "up") {
      const db = drizzle.mock({ schema });
      for (const [name, table] of Object.entries({
        users: schema.users,
        accounts: schema.accounts,
        sessions: schema.sessions,
        verifications: schema.verifications,
        savedSchools: schema.savedSchools,
        schoolNotes: schema.schoolNotes,
      })) {
        const query = db.select().from(table).toSQL();
        const rows = await tx.unsafe(query.sql, query.params as never[]);
        console.log(`${name}: ${rows.length} rows read through the Drizzle schema`);
      }
    }
    if (dryRun) throw new DryRunRollback();
  });
  console.log(`${file} applied`);
} catch (error) {
  if (!(error instanceof DryRunRollback)) throw error;
  console.log(`${file} ran cleanly; rolled back (dry run)`);
} finally {
  await sql.end();
}
