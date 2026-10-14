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

`check` runs Markdownlint CLI2, Python compilation and query-builder tests.
Compilation checks syntax without importing Calibre or executing the plugin.
`python:compile` uses `python3 -m compileall -q __init__.py tests`.
`python:test` uses `python3 -m unittest discover -s tests -v`.
Tests load the actual plugin with fake Calibre and Beautiful Soup imports.
They cover query outputs, missing ISBNs, lookup order and failure propagation.
They do not call the provider or establish host compatibility.
`fix` applies supported Markdown fixes without formatting Python source.
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
