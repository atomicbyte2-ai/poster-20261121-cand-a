// poster-20261121-cand-a: builds entry.png with the Python generator
// (build_entry.py, PIL, deterministic) and copies it to the output dir.
// Validates the gate before copying: PNG, exactly 1024x1024, <= 1 MiB.
import { execFileSync } from "node:child_process";
import { copyFileSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const here = fileURLToPath(new URL(".", import.meta.url));

execFileSync("python3", [join(here, "build_entry.py")], { stdio: "inherit" });

const sourcePath = join(here, "entry.png");
const size = statSync(sourcePath).size;
if (size === 0) {
  throw new Error(`entry.png is empty (0 bytes) at ${sourcePath}`);
}
if (size > 1048576) {
  throw new Error(
    `entry.png too large: ${size} bytes exceeds 1 MiB limit (1048576 bytes)`,
  );
}

const buf = readFileSync(sourcePath);
const PNG_SIG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!buf.subarray(0, 8).equals(PNG_SIG)) {
  throw new Error("entry.png is not a PNG file (bad signature)");
}
if (buf.toString("ascii", 12, 16) !== "IHDR") {
  throw new Error("entry.png has no IHDR chunk where one is expected");
}
const width = buf.readUInt32BE(16);
const height = buf.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  throw new Error(`entry.png is ${width}x${height}, expected 1024x1024`);
}

const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
mkdirSync(outDir, { recursive: true });
copyFileSync(sourcePath, join(outDir, "entry.png"));
console.log(
  `entry.png ${width}x${height} ${size} bytes -> ${join(outDir, "entry.png")}`,
);
