import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");

test("shared Impeccable config is trackable while local config and raw audits are ignored", async () => {
  const [gitignore, configText] = await Promise.all([
    readFile(path.join(root, ".gitignore"), "utf8"),
    readFile(path.join(root, ".impeccable", "config.json"), "utf8"),
  ]);
  const config = JSON.parse(configText);

  assert.match(gitignore, /^\.impeccable\/config\.local\.json$/m);
  assert.match(gitignore, /^\.impeccable\/audits\/$/m);
  assert.doesNotMatch(gitignore, /^\.impeccable\/config\.json$/m);
  assert.deepEqual(config.detector.ignoreRules, []);
  assert.deepEqual(config.detector.ignoreFiles, []);
  assert.equal(config.detector.designSystem.enabled, false);
});
