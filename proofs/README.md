# ISBN lookup request model

[Lookup.tla] models one authenticated metadata lookup in [the plugin].
Both `identify` and `download_cover` share this request path.
The model assumes the identifier map stays fixed during the callback.

| Transition | Plugin behavior |
| --- | --- |
| `BuildRequest` | `get_book_json_url` builds the request URL. |
| `StopBeforeRequest` | The URL is absent or could not be built. |
| `Request` | `get_book_json` calls `download_contents` once. |

TLC checks that the callback makes zero attempts when the ISBN is absent.
TLC also checks that the callback makes at most one attempt.
An ISBN is absent if the map or ISBN value is `None`.
A map without an ISBN key also counts as absent.
The plugin treats empty strings and malformed ISBN text as present.
The plugin has no metadata cache or title/author fallback in either callback.

The request count is measured at the plugin's open/read boundary.
Calibre's image download and `identify`'s public detail-page fetch are separate.
Result parsing, redirects, and provider availability are outside the model.
The [offline transport tests] cover callback responses and failures.

From the repository root, run TLC with Java and the [TLA+ 1.7.4 release] JAR.
The run succeeds when TLC exits with status 0 and reports no errors.

```sh
java -cp /path/to/tla2tools.jar tlc2.TLC -workers 1 -config proofs/Lookup.cfg proofs/Lookup.tla
```

[Lookup.tla]: Lookup.tla
[the plugin]: ../__init__.py
[offline transport tests]: ../tests/test_transport.py
[TLA+ 1.7.4 release]: https://github.com/tlaplus/tlaplus/releases/tag/v1.7.4
