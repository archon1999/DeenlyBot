import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const frontendRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const modulesRoot = path.join(frontendRoot, 'src', 'modules');
const errors = [];

function sourceFiles(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const absolutePath = path.join(directory, entry.name);
    if (entry.isDirectory()) return sourceFiles(absolutePath);
    return /\.(ts|tsx)$/.test(entry.name) ? [absolutePath] : [];
  });
}

for (const entry of fs.readdirSync(modulesRoot, { withFileTypes: true })) {
  if (!entry.isDirectory()) continue;
  const moduleRoot = path.join(modulesRoot, entry.name);
  for (const layer of ['application', 'domain', 'data-access', 'ui']) {
    if (!fs.existsSync(path.join(moduleRoot, layer, 'index.ts'))) {
      errors.push(`${entry.name}/${layer}: missing public index.ts`);
    }
  }
  for (const filePath of sourceFiles(moduleRoot)) {
    const relativePath = path.relative(modulesRoot, filePath).replaceAll('\\', '/');
    const layer = relativePath.split('/')[1];
    const source = fs.readFileSync(filePath, 'utf8');
    const imports = [...source.matchAll(/(?:from\s+|import\s*)['"]([^'"]+)['"]/g)].map(
      (match) => match[1]
    );
    if (['domain', 'application', 'ui'].includes(layer)) {
      if (/\bapiClient\b|\baxios\b|\bfetch\s*\(/.test(source)) {
        errors.push(`${relativePath}: transport calls belong in repository implementations`);
      }
    }
    if (
      layer === 'domain' &&
      imports.some(
        (specifier) =>
          /^(react|@mui|@tanstack|axios)/.test(specifier) ||
          (specifier.startsWith('src/shared/') && !specifier.startsWith('src/shared/domain/')) ||
          /(?:^|\/)(application|data-access|ui)(?:\/|$)/.test(specifier)
      )
    ) {
      errors.push(`${relativePath}: domain depends on framework, transport or presentation`);
    }
    if (
      layer === 'ui' &&
      imports.some((specifier) => /(?:^|\/)data-access(?:\/|$)/.test(specifier))
    ) {
      errors.push(`${relativePath}: UI must call application hooks, not repositories`);
    }
    if (
      layer === 'data-access' &&
      /\bapiClient\b|\baxios\b|\bfetch\s*\(/.test(source) &&
      !relativePath.includes('/repository/')
    ) {
      errors.push(`${relativePath}: network calls must be isolated to repository/`);
    }
  }
}

if (errors.length) {
  console.error(errors.join('\n'));
  process.exitCode = 1;
} else {
  console.log('All Deenly module boundaries are valid.');
}
