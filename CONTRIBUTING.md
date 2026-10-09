# Contributing

Discuss a concrete change in an issue before starting a product repair.
Use the bug report template for observed failures and the improvement template for proposed changes.
State the intended behavior and acceptance criteria so the maintainer can confirm the scope.

## Documentation changes

Check technical claims against [Source implementation](__init__.py) and preserve the exact [plugin marker filename](<plugin-import-name-Korea ISBN Metadata Plugin.txt>).
Describe compatibility declarations separately from executed host checks.
Do not claim that a release archive, packaging command or test suite exists unless the repository actually supplies it.

Put each complete prose sentence on its own source line.
Separate paragraphs with blank lines and preserve normal word spacing.
Preserve code, URLs, quotations, metadata and table syntax.
Prefer `.yaml` when the consuming platform supports it, and verify required filenames and references before renaming existing files.

## Checks

Run the following from the repository root to check whitespace in a tracked change.

```sh
git diff --check
```

- Compare each changed technical claim with the implementation.
- Verify relative links and issue template YAML frontmatter.
- Render changed Markdown and inspect headings, paragraphs, lists and commands.
- Run an available supported Markdown checker and report its exact result.
- For documentation-only changes, confirm that the source and plugin marker are unchanged.

There is no repository test suite or automated check workflow.
A successful documentation check does not prove Calibre compatibility or service behavior.
Record live identify, cover download, API authentication, packaging and host installation as NOTRUN when they were not executed.
Do not import the plugin or call the provider merely to validate prose.

## Safe evidence

Never publish API keys, authenticated request URLs, private host paths or personal data.
The implementation logs API request URLs, so inspect and redact logs before attaching them.
Describe API-key handling and malformed-response findings as separate proposals with isolated inputs and maintainer-approved acceptance before implementing repairs.

## Pull requests and commits

Use the pull request template and link the relevant issue when one exists.
Keep the change within the agreed paths and request an independent review of the complete posted diff.
Report checks as executed, reused, failed, unsupported or NOTRUN.
Explain any reused evidence and why its inputs and tools remain applicable.

Write a concise commit subject, followed by a blank line and a substantive body.
Explain the reason, changes, actual checks and material failures or NOTRUN limits.
Apply the sentence-per-source-line rule to the body.
