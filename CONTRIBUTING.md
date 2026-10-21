# Contributing

Discuss a concrete change in an issue before starting a product repair.
Use [Bug reports](.github/ISSUE_TEMPLATE/bug_report.md) for observed failures.
Use [Improvement proposals](.github/ISSUE_TEMPLATE/improvement.md) for changes.
See [Working as an agent](#working-as-an-agent) for task scope and acceptance.

## Working as an agent

Before editing, state the outcome, affected paths, exclusions and observable acceptance.
Keep each task to one bounded change within the agreed paths.
Verify each bounded change before starting another.
Preserve each task's evidence requirements.
Label checks run in this task `ACTUAL`.
Use `REUSED` only if relevant behavior, inputs and configuration are unchanged.
Relevant tools must also remain unchanged.
Explain why the evidence still applies.
Label failed checks `FAILED`.
Label checks not run `NOTRUN` and state why.
Stop discovery when evidence supports the implementation decision.

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
- Report the exact Markdownlint CLI2 and Python compilation results.
- For documentation-only changes, confirm the source and marker are unchanged.

`check` runs Ultracite and Markdownlint CLI2.
It also compiles Python and runs isolated unit tests.
Ultracite runs Oxlint and Oxfmt with the repository presets.
Oxfmt excludes Markdown, which stays under Markdownlint CLI2.
`docs/no-box-drawing` rejects Unicode box-drawing characters in Markdown.
Compilation checks syntax without importing Calibre or executing the plugin.
`python:compile` uses `python3 -m compileall -q __init__.py tests`.
`python:test` uses `python3 -m unittest discover -s tests -v`.
Tests load the actual plugin with fake Calibre and Beautiful Soup imports.
They cover query outputs, missing ISBNs, lookup order and failure propagation.
They also cover callback and invalid-response behavior.
They do not call the provider or establish host compatibility.
`fix` runs Ultracite fixes and supported Markdown fixes.
Neither formatter changes Python source.
The box-drawing rule reports violations without an automatic fix.
Review fixes and run `check` again before committing.

Installation runs `prepare` and installs Husky at the Git root.
The pre-commit hook invokes `pnpm run pre-commit`.
The pre-push hook invokes `pnpm run pre-push`.
Both scripts run `check`, and failures block their Git operation.
Run `pnpm run prepare` to restore hooks after a checkout or local Git reset.
Check existing hook ownership before installing in a configured checkout.
Compose any existing required hooks rather than replacing them silently.
Test hook changes with actual commits and pushes in disposable repositories.
Include a failing check and verify that each Git operation is blocked.

The query-builder tests run through both Git hook gates.
There is no automated check workflow.
A successful check does not prove Calibre compatibility or service behavior.
Record unexecuted identify, cover and API authentication checks as NOTRUN.
Do the same for packaging and host installation.
Do not import the plugin or call the provider merely to validate prose.

## Safe evidence

Never publish API keys, authenticated URLs, private host paths or personal data.
Logs may include response data, identifiers and detail-page URLs.
Inspect and redact logs before sharing them.
Scope product repairs separately and verify each with isolated inputs.
Set acceptance criteria before implementing each repair.

## Development lifecycle

See [Working as an agent](#working-as-an-agent).
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

Use the [pull request template](.github/pull_request_template.md).
Link the relevant issue when one exists.
See [Working as an agent](#working-as-an-agent) for evidence labels and scope.
Request independent review of the complete posted diff.

Write a concise commit subject, followed by a blank line and a substantive body.
Explain the reason, changes, actual checks and material failures or NOTRUN limits.
Apply the sentence-per-source-line rule to the body.

[plugin-marker]: <plugin-import-name-Korea ISBN Metadata Plugin.txt>
[pstack]: https://github.com/cursor/plugins/tree/main/pstack
[sinon-harness]: https://github.com/ririnto/sinon/tree/main/plugins/harness/tooling
