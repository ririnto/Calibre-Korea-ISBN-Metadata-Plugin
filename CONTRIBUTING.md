# Contributing

Discuss a concrete change in an issue before starting a product repair.
Use the bug report template for observed failures.
Use the improvement template for proposed changes.
State the intended behavior and acceptance criteria to establish scope.

## Documentation changes

Check technical claims against the [source](__init__.py).
Preserve the exact [plugin marker filename][plugin-marker].
Describe compatibility declarations separately from executed host checks.
Only claim release archives, packaging commands or tests that actually exist.

Put each complete prose sentence on its own source line.
Separate paragraphs with blank lines and preserve normal word spacing.
Preserve code, URLs, quotations, metadata and table syntax.
Prefer `.yaml` when the consuming platform supports it.
Verify required filenames and references before renaming files.

Keep Markdownlint's Git ignore selection enabled with `gitignore: true`.
Use compact Markdown tables and recursively sorted configuration keys.
Never suppress, disable or weaken lint rules to make a change pass.

## Dependencies

Define dependency versions in the default `pnpm-workspace.yaml` catalog.
Use `^x.y.z` caret ranges.
Reference those entries with `catalog:` in `package.json`.
Regenerate and commit `pnpm-lock.yaml` when changing the catalog.
Prefer officially supported LTS releases, or stable releases when no LTS line exists.
Verify compatibility with the declared runtime and tooling before selecting versions.
Do not add version-plus-hash pins or remove lockfile integrity checks.

## Checks

Use Node.js 24 LTS and the pnpm version selected by `packageManager`.
Have Python 3 available as `python3` with support for the plugin's syntax.
Run these commands from the repository root.

```sh
pnpm install --frozen-lockfile
pnpm run check
git diff --check
```

- Compare each changed technical claim with the implementation.
- Verify relative links and issue template YAML frontmatter.
- Render changed Markdown and inspect headings, paragraphs, lists and commands.
- Report the exact Markdownlint CLI2, Ultracite and Python compilation results.
- For documentation-only changes, confirm the source and marker are unchanged.

`pnpm run check` runs Markdownlint CLI2 and Ultracite.
It also runs Python compilation and all 18 offline tests.
Compilation checks syntax without importing Calibre or executing the plugin.
`python:compile` uses `python3 -m compileall -q __init__.py tests`.
`python:test` uses `python3 -m unittest discover -s tests -v`.
All 18 offline tests use fake Calibre and Beautiful Soup imports.
They load the actual plugin.
They cover query-builder outputs, missing ISBNs, lookup order and failure propagation.
They test identify and cover transport, malformed responses and safe logging.
They do not call the provider or establish host compatibility.
Ultracite is the sole executable caller of Oxlint and Oxfmt.
Markdownlint CLI2 remains the Markdown semantic gate.
`pnpm run fix` uses Markdownlint CLI2 and Ultracite.
It does not format Python or Markdown through Oxfmt.
Review fixes and run `pnpm run check` again before committing.

Installation runs `prepare` and installs Husky at the Git root.
The pre-commit hook invokes `pnpm run pre-commit`.
The pre-push hook invokes `pnpm run pre-push`.
Both scripts run `check`, and failures block their Git operation.
Run `pnpm run prepare` to restore hooks after a checkout or local Git reset.
Check existing hook ownership before installing in a configured checkout.
Compose any existing required hooks rather than replacing them silently.
Test hook changes with actual commits and pushes in disposable repositories.
Include a failing check and verify that each Git operation is blocked.

All 18 offline tests run through both Git hook gates.
There is no automated check workflow.
A successful check does not prove Calibre compatibility or service behavior.
Record unexecuted identify, cover and API authentication checks as NOT RUN.
Do the same for packaging and host installation.
Do not import the plugin or call the provider merely to validate prose.

## Safe evidence

Never publish API keys, authenticated URLs, private host paths or personal data.
The implementation logs API request URLs.
Inspect and redact logs before attaching them.
Propose API-key and malformed-response repairs separately with isolated inputs.
Establish acceptance before implementing those repairs.

## Development lifecycle

Define the outcome, affected paths, exclusions and observable acceptance first.
Stop discovery once evidence supports the implementation decision.
Complete one bounded change and verify it before adding another.
For defects, reproduce the trigger and fix the cause before updating guidance.
Test behavior through real entry points and assert the result users observe.
Assert behavior and document structure without hard-pinning prose wording in tests.
Prefer condition inversion over mid-function `return`, `continue` or `break`.
Preserve equivalent behavior and avoid deeper nesting.
Keep automated checks separate from host and live service evidence.
Finish authorized delivery with review, integration and main branch readback.
Remove disposable resources only after confirming ownership and preservation.

These rules apply the [pstack lifecycle principles][pstack] to this plugin.
The script and hook surface follows the [Sinon harness tooling][sinon-harness].

## Pull requests and commits

Use the pull request template and link the relevant issue when one exists.
Keep changes within the agreed paths.
Request independent review of the complete posted diff.
Report checks as executed, reused, failed, unsupported or NOTRUN.
Explain any reused evidence and why its inputs and tools remain applicable.

Write a concise commit subject, followed by a blank line and a substantive body.
Explain the reason, changes, actual checks and material failures or NOTRUN limits.
Apply the sentence-per-source-line rule to the body.

[plugin-marker]: <plugin-import-name-Korea ISBN Metadata Plugin.txt>
[pstack]: https://github.com/cursor/plugins/tree/main/pstack
[sinon-harness]: https://github.com/ririnto/sinon/tree/main/plugins/harness/tooling
