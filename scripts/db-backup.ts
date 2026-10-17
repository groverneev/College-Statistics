import { mkdir } from "node:fs/promises";
import postgres from "postgres";

const TABLES = ["User", "Account", "SavedSchool", "SchoolNote"] as const;
const [command = "", file] = process.argv.slice(2);
// Keep "timestamp without time zone" values as the exact strings Postgres stores; parsing them
// into Date objects would shift them by the local time zone.
const rawTimestamp = {
  to: 1114,
  from: [1114],
  serialize: (x: string) => x,
  parse: (x: string) => x,
};
const sql = postgres(process.env.DATABASE_URL!, {
  max: 1,
  prepare: false,
  types: { rawTimestamp },
});

type Backup = {
  takenAt: string;
  columns: Record<string, { column_name: string; data_type: string }[]>;
  rows: Record<string, Record<string, unknown>[]>;
};

async function snapshot(db: postgres.Sql | postgres.TransactionSql): Promise<Backup> {
  const backup: Backup = { takenAt: new Date().toISOString(), columns: {}, rows: {} };
  for (const table of TABLES) {
    backup.columns[table] = await db`
      SELECT column_name, data_type FROM information_schema.columns
      WHERE table_schema = 'public' AND table_name = ${table} ORDER BY ordinal_position`;
    backup.rows[table] = await db`SELECT * FROM ${db(table)} ORDER BY id`;
  }
  return backup;
}

async function restore(tx: postgres.TransactionSql, backup: Backup) {
  await tx`TRUNCATE "SchoolNote", "SavedSchool", "Account", "User"`;
  for (const table of TABLES) {
    const rows = backup.rows[table];
    if (rows.length > 0) await tx`INSERT INTO ${tx(table)} ${tx(rows)}`;
  }
}

function firstMismatch(a: Backup, b: Backup): string | null {
  for (const table of TABLES) {
    if (a.rows[table].length !== b.rows[table].length) return `${table} row count`;
    for (const [i, row] of b.rows[table].entries()) {
      for (const key of Object.keys(row)) {
        if (JSON.stringify(a.rows[table][i][key]) !== JSON.stringify(row[key]))
          return `${table}[${i}].${key}`;
      }
    }
  }
  return null;
}

try {
  if (command === "save") {
    await mkdir("backups", { recursive: true });
    const backup = await snapshot(sql);
    const out = file ?? `backups/db-${backup.takenAt.replace(/[:.]/g, "-")}.json`;
    await Bun.write(out, JSON.stringify(backup, null, 2));
    console.log(`saved ${out}: ${TABLES.map((t) => `${t}=${backup.rows[t].length}`).join(" ")}`);
  } else if (command === "verify" || command === "restore") {
    if (!file) throw new Error(`usage: bun scripts/db-backup.ts ${command} <file>`);
    const backup: Backup = await Bun.file(file).json();
    class Rollback extends Error {}
    try {
      await sql.begin(async (tx) => {
        await restore(tx, backup);
        const roundTrip: Backup = JSON.parse(JSON.stringify(await snapshot(tx)));
        const mismatch = firstMismatch(roundTrip, backup);
        if (mismatch) throw new Error(`restored data does not match the backup at ${mismatch}`);
        console.log(`restore of ${file} reproduces the backup exactly`);
        if (command === "verify") throw new Rollback();
      });
      console.log("restored");
    } catch (error) {
      if (!(error instanceof Rollback)) throw error;
      console.log("rolled back (verify only)");
    }
  } else {
    console.error("usage: bun scripts/db-backup.ts <save [file] | verify <file> | restore <file>>");
    process.exit(1);
  }
} finally {
  await sql.end();
}
