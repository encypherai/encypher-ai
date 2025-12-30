import { readFile, stat } from 'node:fs/promises';
import path from 'node:path';

import { DashboardLayout } from '../../../components/layout/DashboardLayout';
import { PublisherIntegrationGuideClient } from './PublisherIntegrationGuideClient';

async function isDirectory(dirPath: string): Promise<boolean> {
  try {
    const info = await stat(dirPath);
    return info.isDirectory();
  } catch {
    return false;
  }
}

async function isFile(filePath: string): Promise<boolean> {
  try {
    const info = await stat(filePath);
    return info.isFile();
  } catch {
    return false;
  }
}

async function findRepoRoot(startDir: string): Promise<string> {
  let current = path.resolve(startDir);
  const { root } = path.parse(current);

  // Look for the monorepo root markers.
  while (true) {
    const appsDir = path.join(current, 'apps');
    const gitDir = path.join(current, '.git');
    const pyproject = path.join(current, 'pyproject.toml');

    // Use file existence checks to avoid throwing if permissions or missing.
    const hasApps = await isDirectory(appsDir);
    const hasGit = await isDirectory(gitDir);
    const hasPyproject = await isFile(pyproject);

    if (hasApps && hasGit && hasPyproject) return current;

    if (current === root) {
      throw new Error(`Could not locate repo root from ${startDir}`);
    }

    current = path.dirname(current);
  }
}

async function getGuidePath(): Promise<string> {
  const guessRoot = path.resolve(process.cwd(), '..', '..', '..');
  const guessPath = path.join(guessRoot, 'docs', 'guides', 'publisher-integration-guide.md');
  if (await isFile(guessPath)) return guessPath;

  const repoRoot = await findRepoRoot(process.cwd());
  return path.join(repoRoot, 'docs', 'guides', 'publisher-integration-guide.md');
}

export default async function PublisherIntegrationGuidePage() {
  const guidePath = await getGuidePath();
  let markdown = '';
  try {
    markdown = await readFile(guidePath, 'utf8');
  } catch {
    markdown = `# Publisher Integration Guide\n\nGuide file not found. Expected at: \`${guidePath}\`\n`;
  }

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto">
        <PublisherIntegrationGuideClient markdown={markdown} />
      </div>
    </DashboardLayout>
  );
}
