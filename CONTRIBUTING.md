# Contributing

Define the change in an issue before implementation.
Use [Bug reports](.github/ISSUE_TEMPLATE/bug_report.md) for observed failures.
Use [Improvement proposals](.github/ISSUE_TEMPLATE/improvement.md) for changes.

## Working as an agent

Before editing, state the outcome, paths, exclusions and deliverables.
Define observable acceptance and required evidence.
Keep each task to one bounded change within its authorized scope.
Verify each bounded change before starting another.
Stop discovery when evidence supports the implementation decision.

Report each check's command, result and coverage.
Use `ACTUAL` for checks run in this task.
Use `REUSED` only if relevant behavior, inputs and configuration are unchanged.
Relevant tools must also remain unchanged.
Explain why reused evidence still applies.
Label failed checks `FAILED`.
Label blocked requirements `BLOCKED` and state the next action.
Label checks not run `NOTRUN` and state why.
When acceptance remains unmet, report remaining work instead of completion.

## Documentation changes

Check technical claims against the [source](__init__.py).
Preserve the exact [plugin marker filename][plugin-marker].
Distinguish source declarations from executed compatibility checks.
Document only existing release archives, packaging commands and tests.

Put each complete prose sentence on its own source line.
Separate paragraphs with blank lines and preserve normal word spacing.
Preserve code, URLs, quotations, metadata and table syntax.
Prefer `.yaml` when the consuming platform supports it.
Verify required filenames and references before renaming files.

Keep Markdownlint's Git ignore selection enabled with `gitignore: true`.
Use compact Markdown tables.
Sort configuration keys recursively unless a formatter specifies their order.
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

Use Node.js 26 and the pnpm version declared in `package.json`.
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

Run `check` for lint, format, syntax and isolated unit test validation.
Keep Oxfmt's Markdown exclusion and validate Markdown with Markdownlint CLI2.
Reject Unicode box-drawing characters in Markdown with `docs/no-box-drawing`.
Use `python:compile` to check syntax without executing the plugin.
Treat isolated unit tests as query and callback coverage.
Do not infer host or live provider validation from fake imports.
After `fix`, review changes and rerun `check` before committing.
Do not expect `fix` to repair box-drawing violations or format Python.

Check existing hook ownership before installation.
Compose required hooks instead of replacing them.
Run `pnpm run prepare` to restore Husky hooks after a checkout or local Git reset.
Require both `pre-commit` and `pre-push` to run their maintained `check` gate.
The hooks invoke `pnpm run pre-commit` and `pnpm run pre-push` directly.
Test hook changes with actual commits and pushes in disposable repositories.
Include a failing check and verify that each Git operation is blocked.

Keep local check results separate from workflow and host evidence.
Record identify, cover and API authentication checks as `NOTRUN` unless run.
Do the same for packaging and host installation.
Do not import the plugin or call the provider merely to validate prose.

## Safe evidence

Never publish API keys, authenticated URLs, private host paths or personal data.
Inspect logs for response data, identifiers and detail-page URLs.
Redact sensitive content before sharing logs or publishing evidence.

## Development lifecycle

For defects, reproduce the trigger and fix the cause before updating guidance.
Test repairs through real entry points with isolated inputs.
Assert observable results.
Assert behavior and document structure without hard-pinning prose wording in tests.
Prefer condition inversion over mid-function `return`, `continue` or `break`.
Preserve equivalent behavior and avoid deeper nesting.
For authorized delivery, obtain independent review before normal integration.
Read back the named main branch after integration.
Remove disposable resources only after confirming ownership and preservation.

## Pull requests and commits

Use the [pull request template](.github/pull_request_template.md).
Link the related issue.
Request independent review of the complete posted diff.

Write a concise commit subject, followed by a blank line and a substantive body.
Explain the reason, changes, actual checks and material failures or NOTRUN limits.
Apply the sentence-per-source-line rule to the body.

[plugin-marker]: <plugin-import-name-Korea ISBN Metadata Plugin.txt>
