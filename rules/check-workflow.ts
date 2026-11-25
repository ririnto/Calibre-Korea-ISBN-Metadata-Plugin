import { readdirSync, readFileSync } from "node:fs";

import { parse } from "yaml";

import packageConfig from "../package.json" with { type: "json" };

const isMapping = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null && !Array.isArray(value);

const readWorkflow = (workflowPath: string): Record<string, unknown> => {
  const workflow: unknown = parse(readFileSync(workflowPath, "utf-8"));
  return isMapping(workflow) ? workflow : {};
};

const workflowDirectory = ".github/workflows";
const contributorWorkflowPath = `${workflowDirectory}/contributor-checks.yaml`;
const contributorWorkflow = readWorkflow(contributorWorkflowPath);
const events = contributorWorkflow.on ?? null;

if (
  events !== "pull_request" &&
  !(Array.isArray(events) && events.includes("pull_request")) &&
  !(isMapping(events) && Object.hasOwn(events, "pull_request"))
) {
  throw new Error(
    `${contributorWorkflowPath}: workflow/pull-request requires a pull_request trigger`
  );
}

const metadataByReference = new Map(
  Object.entries(packageConfig.workflowChecks.actionDefaults).filter(
    ([, { commit }]) => /^[a-f0-9]{40}$/u.test(commit)
  )
);
const workflowNames = readdirSync(workflowDirectory, { withFileTypes: true })
  .filter(
    (entry) =>
      entry.isFile() &&
      (entry.name.endsWith(".yaml") || entry.name.endsWith(".yml"))
  )
  .map((entry) => entry.name)
  .toSorted();

for (const workflowName of workflowNames) {
  const workflowPath = `${workflowDirectory}/${workflowName}`;
  const { jobs } =
    workflowPath === contributorWorkflowPath
      ? contributorWorkflow
      : readWorkflow(workflowPath);
  if (!isMapping(jobs)) {
    continue;
  }
  for (const job of Object.values(jobs)) {
    if (!isMapping(job) || !Array.isArray(job.steps)) {
      continue;
    }
    const steps: readonly unknown[] = job.steps;
    for (const step of steps) {
      if (
        !isMapping(step) ||
        typeof step.uses !== "string" ||
        !isMapping(step.with)
      ) {
        continue;
      }
      for (const [input, defaultValue] of Object.entries(
        metadataByReference.get(step.uses)?.defaults ?? {}
      )) {
        const value = step.with[input];
        if (
          (typeof value === "string" ||
            typeof value === "boolean" ||
            typeof value === "number") &&
          String(value) === defaultValue &&
          !(typeof value === "string" && value.includes("${{"))
        ) {
          process.stderr.write(
            `${workflowPath}: workflow/no-default-inputs (R35): ${step.uses} input ${input} equals its documented default. Omit this input.\n`
          );
          process.exitCode = 1;
        }
      }
    }
  }
}
