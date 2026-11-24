import { readFileSync } from "node:fs";

import { parse } from "yaml";

const workflowPath = ".github/workflows/contributor-checks.yaml";
const workflow: unknown = parse(readFileSync(workflowPath, "utf-8"));
const events =
  typeof workflow === "object" && workflow !== null && "on" in workflow
    ? workflow.on
    : null;

if (
  events !== "pull_request" &&
  !(Array.isArray(events) && events.includes("pull_request")) &&
  !(
    typeof events === "object" &&
    events !== null &&
    Object.hasOwn(events, "pull_request")
  )
) {
  throw new Error(
    `${workflowPath}: workflow/pull-request requires a pull_request trigger`
  );
}
