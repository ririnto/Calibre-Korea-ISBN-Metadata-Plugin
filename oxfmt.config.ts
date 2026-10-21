import { defineConfig } from "oxfmt";
import ultracite from "ultracite/oxfmt";

/**
 * Repository Oxfmt configuration.
 */
export default defineConfig({
  ...ultracite,
  ignorePatterns: [...(ultracite.ignorePatterns ?? []), "**/*.md"],
  trailingComma: "none"
});
