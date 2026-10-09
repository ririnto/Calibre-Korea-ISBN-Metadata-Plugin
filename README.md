# Korea ISBN Metadata Plugin

This Calibre metadata source retrieves book metadata and cover images using ISBN identifiers and National Library of Korea endpoints.
The implementation is in [Source implementation](__init__.py).

## Requirements and configuration

The source declares plugin version 1.0.0 and a minimum Calibre version of 7.0.0.
It declares Windows, macOS (`osx`) and Linux support.
These are source declarations, not results of executed compatibility tests.

The plugin depends on the Calibre host APIs and imports Beautiful Soup as `bs4`.
It is not a standalone Python application.
This repository provides no dependency manifest, installation archive or packaging command.

Configure the plugin's string option named `api_key` in the Calibre host with your National Library of Korea API key.
The configuration check reads this option, and the API query sends its value as `cert_key`.
Do not commit or publish your key.

Provide an `isbn` book identifier before requesting metadata or a cover.
The lookup URL builders require this identifier.
Title and author arguments do not provide a fallback search.

## Declared behavior

- The `identify` capability reads the first record from the ISBN API response.
- The `cover` capability downloads the image referenced by that record's `TITLE_URL`.
- Metadata includes title, authors, publisher, publication date, series and ISBN fields when supplied by the response.
- The book detail page can supply tags, DOI, language and HTML comments.

The API endpoint used by the source is `https://www.nl.go.kr/seoji/SearchApi.do`.
The detail page endpoint is `https://nl.go.kr/seoji/contents/S80100000000.do`.
Availability and successful authentication have not been verified by this documentation change.

## Repository files

| File | Purpose |
| :--- | --- |
| [Source implementation](__init__.py) | Calibre metadata source implementation. |
| [plugin-import-name-Korea ISBN Metadata Plugin.txt](<plugin-import-name-Korea ISBN Metadata Plugin.txt>) | Empty plugin import marker with its exact filename. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution scope and validation guidance. |
| [.github/ISSUE_TEMPLATE](.github/ISSUE_TEMPLATE) | Bug report and improvement templates. |
| [.github/pull_request_template.md](.github/pull_request_template.md) | Pull request evidence template. |

## Validation limits

The repository contains no test suite or automated check workflow.
Documentation checks can compare claims with the source, verify relative links and template frontmatter, render Markdown and run `git diff --check`.
They do not establish runtime correctness.

Live identify, cover download, API authentication, packaging and Calibre host installation were NOTRUN for this documentation delivery.
Calibre was unavailable in the documentation executor.

## Reporting problems

Use the repository's bug report or improvement template and follow [CONTRIBUTING.md](CONTRIBUTING.md).
Review logs before sharing them because the source logs API URLs that can contain `cert_key`.
Remove keys, private paths and personal book data from reports.
