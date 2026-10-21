import { defineConfig } from "oxlint";
import core from "ultracite/oxlint/core";

/**
 * Repository Oxlint configuration.
 */
export default defineConfig({
  extends: [core],
  ignorePatterns: core.ignorePatterns
});
