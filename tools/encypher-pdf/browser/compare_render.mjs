import fs from 'node:fs/promises';
import path from 'node:path';
import { PNG } from 'pngjs';
import pixelmatch from 'pixelmatch';

async function readPng(filePath) {
  const buffer = await fs.readFile(filePath);
  return PNG.sync.read(buffer);
}

async function main() {
  const [, , actualPathArg, baselinePathArg, diffPathArg] = process.argv;
  if (!actualPathArg || !baselinePathArg || !diffPathArg) {
    console.error('Usage: node compare_render.mjs <actual.png> <baseline.png> <diff.png>');
    process.exit(1);
  }

  const actualPath = path.resolve(actualPathArg);
  const baselinePath = path.resolve(baselinePathArg);
  const diffPath = path.resolve(diffPathArg);

  const actual = await readPng(actualPath);
  const baseline = await readPng(baselinePath);

  if (actual.width !== baseline.width || actual.height !== baseline.height) {
    console.error(JSON.stringify({
      ok: false,
      reason: 'dimension-mismatch',
      actual: { width: actual.width, height: actual.height },
      baseline: { width: baseline.width, height: baseline.height },
    }, null, 2));
    process.exit(1);
  }

  const diff = new PNG({ width: actual.width, height: actual.height });
  const mismatchPixels = pixelmatch(
    actual.data,
    baseline.data,
    diff.data,
    actual.width,
    actual.height,
    { threshold: 0.1 }
  );

  await fs.writeFile(diffPath, PNG.sync.write(diff));

  const totalPixels = actual.width * actual.height;
  const mismatchRatio = totalPixels ? mismatchPixels / totalPixels : 0;
  const result = {
    ok: mismatchRatio <= 0.005,
    mismatchPixels,
    totalPixels,
    mismatchRatio,
    diffPath,
  };

  if (!result.ok) {
    console.error(JSON.stringify(result, null, 2));
    process.exit(1);
  }

  console.log(JSON.stringify(result, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
