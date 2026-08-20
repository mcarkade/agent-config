import { readdir, readFile, realpath, stat, writeFile } from "node:fs/promises";
import path from "node:path";

const EM_DASH = "\u2014";

async function exists(candidate) {
  try {
    await stat(candidate);
    return true;
  } catch (error) {
    if (error?.code === "ENOENT") return false;
    throw error;
  }
}

async function collectSkillFiles(root, files, visitedDirectories) {
  if (!(await exists(root))) return;

  const rootStat = await stat(root);
  if (rootStat.isFile()) {
    if (path.basename(root) === "SKILL.md") files.add(await realpath(root));
    return;
  }
  if (!rootStat.isDirectory()) return;

  const canonicalRoot = await realpath(root);
  if (visitedDirectories.has(canonicalRoot)) return;
  visitedDirectories.add(canonicalRoot);

  const entries = await readdir(root);
  for (const entry of entries) {
    await collectSkillFiles(path.join(root, entry), files, visitedDirectories);
  }
}

const roots = process.argv.slice(2);
if (roots.length === 0) {
  throw new Error("Pass at least one skill root.");
}

const files = new Set();
const visitedDirectories = new Set();
for (const root of roots) {
  await collectSkillFiles(path.resolve(root), files, visitedDirectories);
}

let changedFiles = 0;
let replacements = 0;

for (const file of files) {
  const original = await readFile(file, "utf8");
  const matches = original.split(EM_DASH).length - 1;
  if (matches === 0) continue;

  const updated = original
    .replaceAll(` ${EM_DASH} `, ", ")
    .replaceAll(EM_DASH, ",");
  await writeFile(file, updated, "utf8");
  changedFiles += 1;
  replacements += matches;
}

console.log(`Removed ${replacements} em dashes from ${changedFiles} SKILL.md files.`);
