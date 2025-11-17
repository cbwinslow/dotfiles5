#!/usr/bin/env node
/**
 * Export Postman environment variable `discovered_endpoints` to a JSON file.
 *
 * Usage:
 *   node export_endpoints.js <env-json-path> <output-path>
 */

const fs = require('fs');

function main() {
  const [,, envPath, outPath] = process.argv;
  if (!envPath || !outPath) {
    console.error('Usage: node export_endpoints.js <env.json> <output.json>');
    process.exit(1);
  }

  const env = JSON.parse(fs.readFileSync(envPath, 'utf8'));
  const values = env.values || [];
  const found = values.find(v => v.key === 'discovered_endpoints');

  if (!found || !found.value) {
    console.error('No discovered_endpoints variable found in env file.');
    process.exit(1);
  }

  let endpoints;
  try {
    endpoints = JSON.parse(found.value);
  } catch (e) {
    console.error('Failed to parse discovered_endpoints JSON:', e.message);
    process.exit(1);
  }

  // Basic de-dup by method+path+status
  const unique = {};
  for (const ep of endpoints) {
    const key = `${ep.method}:${ep.path}:${ep.status}`;
    unique[key] = ep;
  }

  fs.writeFileSync(outPath, JSON.stringify(Object.values(unique), null, 2));
  console.log(`Wrote ${Object.keys(unique).length} unique endpoints to ${outPath}`);
}

if (require.main === module) {
  main();
}
