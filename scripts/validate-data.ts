import { readdir } from "node:fs/promises";
import { join } from "node:path";
import { z } from "zod";
import { schoolDataSchema } from "../src/lib/schoolSchema";

const dir = join(import.meta.dir, "../src/data/schools");
const files = (await readdir(dir)).filter((f) => f.endsWith(".json"));
let failures = 0;

for (const file of files) {
  const result = schoolDataSchema.safeParse(await Bun.file(join(dir, file)).json());
  if (!result.success) {
    failures++;
    console.error(`${file}\n${z.prettifyError(result.error)}\n`);
  } else if (`${result.data.slug}.json` !== file) {
    failures++;
    console.error(`${file}: slug "${result.data.slug}" does not match file name\n`);
  }
}

if (failures > 0) {
  console.error(`${failures} of ${files.length} school files failed validation`);
  process.exit(1);
}
console.log(`${files.length} school files valid`);
