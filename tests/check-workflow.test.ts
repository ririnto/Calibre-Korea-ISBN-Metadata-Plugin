import { doesNotMatch, equal, match } from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

await test("rejects literal inputs equal to approved defaults for the exact action reference", (t) => {
  const cwd = mkdtempSync(path.join(tmpdir(), "workflow-check-"));
  t.after(() => {
    rmSync(cwd, { recursive: true });
  });

  const workflowDirectory = path.join(cwd, ".github", "workflows");
  mkdirSync(workflowDirectory, { recursive: true });
  const workflowPath = path.join(workflowDirectory, "contributor-checks.yaml");
  const releasePath = path.join(workflowDirectory, "release.yml");
  const check = () =>
    spawnSync(
      process.execPath,
      [fileURLToPath(new URL("../rules/check-workflow.ts", import.meta.url))],
      { cwd, encoding: "utf-8" }
    );

  const controls = `on: pull_request
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: pnpm/action-setup@v6
        with:
          cache: true
          cache_dependency_path: \${{ 'pnpm-lock.yaml' }}
      - uses: pnpm/action-setup@v5
        with:
          cache_dependency_path: pnpm-lock.yaml
      - uses: example/unknown-action@v1
        with:
          cache_dependency_path: pnpm-lock.yaml
      - uses: actions/setup-node@v7
        with:
          package-manager-cache: true
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0
`;
  const release = `on: push
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0
`;
  writeFileSync(workflowPath, controls);
  writeFileSync(releasePath, release);
  const passing = check();
  equal(passing.status, 0, passing.stderr);

  writeFileSync(
    workflowPath,
    `${controls}      - uses: pnpm/action-setup@v6
        with:
          cache: false
          cache_dependency_path: pnpm-lock.yaml
          run_install: null
      - uses: actions/checkout@v7
        with:
          fetch-depth: 1
`
  );
  const failing = check();
  equal(failing.status, 1, failing.stderr);
  match(
    failing.stderr,
    /workflow\/no-default-inputs \(R35\).*pnpm\/action-setup@v6.*cache_dependency_path/u
  );
  match(
    failing.stderr,
    /workflow\/no-default-inputs \(R35\).*pnpm\/action-setup@v6.*input cache /u
  );
  doesNotMatch(failing.stderr, /run_install/u);
  match(
    failing.stderr,
    /workflow\/no-default-inputs \(R35\).*actions\/checkout@v7.*fetch-depth/u
  );

  writeFileSync(workflowPath, controls);
  writeFileSync(
    releasePath,
    release.replace("fetch-depth: 0", "fetch-depth: 1")
  );
  const failingRelease = check();
  equal(failingRelease.status, 1, failingRelease.stderr);
  match(
    failingRelease.stderr,
    /\.github\/workflows\/release\.yml: workflow\/no-default-inputs \(R35\).*actions\/checkout@v7.*fetch-depth/u
  );

  writeFileSync(workflowPath, controls.replace("on: pull_request", "on: push"));
  const missingPullRequest = check();
  equal(missingPullRequest.status, 1, missingPullRequest.stderr);
  match(
    missingPullRequest.stderr,
    /\.github\/workflows\/contributor-checks\.yaml: workflow\/pull-request/u
  );
});
