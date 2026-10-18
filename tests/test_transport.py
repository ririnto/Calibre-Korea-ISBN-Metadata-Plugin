"""
Exercise authenticated callbacks with offline Calibre contract fixtures.
These fixtures model browser policy and cloning, not installed TLS behavior.
"""

from datetime import datetime
import importlib.util
import json
from pathlib import Path
from queue import Queue
import ssl
import sys
from threading import Event
import traceback
from types import ModuleType
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit


class _Log:
    def __init__(self):
        self.messages = []
        self.exceptions = []

    def info(self, *args):
        self.messages.append(" ".join(map(str, args)))

    debug = __call__ = info

    def exception(self, *args, **kwargs):
        rendered = traceback.format_exc(kwargs.pop("limit", None))
        self.exceptions.append(" ".join(map(str, args)) + "\n" + rendered)
        self.info(*args)
        self.info(rendered)


class _Metadata:
    def __init__(self, title, authors):
        self.title, self.authors = title, authors
        self.identifiers = {}

    def set_identifier(self, typ, val):
        self.identifiers[typ] = val


class _Browser:
    def __init__(self, owner, context):
        self.owner, self.context = owner, context

    def clone_browser(self):
        return _Browser(self.owner, self.context)

    def open_novisit(self, url_or_request, timeout):
        self.owner.requests.append((url_or_request, timeout, self))
        if "SearchApi.do" in url_or_request and self.owner.failure_stage == "open":
            self.owner.fail(url_or_request)
        return _Response(self.owner, url_or_request)


class _Response:
    def __init__(self, owner, url):
        self.owner, self.url = owner, url

    def read(self):
        if "SearchApi.do" in self.url:
            if self.owner.failure_stage == "read":
                self.owner.fail(self.url)
            return self.owner.payload
        return b"cover bytes" if self.url.endswith("cover.jpg") else b"<html></html>"


class _Source:
    ignore_ssl_errors = False

    def __init__(self):
        self._browser = None
        self.requests, self.cleaned = [], []
        self.failure_stage = self.error_kind = None

    @property
    def browser(self):
        if self._browser is None:
            context = ssl.create_default_context()
            if self.ignore_ssl_errors:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            self._browser = _Browser(self, context)
        return self._browser.clone_browser()

    def clean_downloaded_metadata(self, mi):
        self.cleaned.append(mi)

    def download_image(self, url, timeout, log, result_queue):
        try:
            ans = self.browser.open_novisit(url, timeout=timeout).read()
            result_queue.put((self, ans))
            log("Downloaded cover from: %s" % url)
        except Exception:
            log.exception("Failed to download cover from: %r" % url)

    def fail(self, url):
        if self.error_kind == "http":
            raise HTTPError(url, 403, url, {}, None)
        if self.error_kind == "tls":
            raise URLError(ssl.SSLCertVerificationError(url))
        if self.error_kind == "nested":
            try:
                raise URLError(url)
            except URLError:
                raise OSError("transport failed")
        raise URLError(url)


class _EmptyBookPage:
    text = ""

    def __init__(self, markup, features):
        if markup != "<html></html>" or features != "html.parser":
            raise ValueError("Unexpected offline detail-page fixture")

    def select(self, selector):
        return []


def _load_plugin():
    modules = {name: ModuleType(name) for name in (
        "bs4", "calibre", "calibre.ebooks", "calibre.ebooks.metadata",
        "calibre.ebooks.metadata.book", "calibre.ebooks.metadata.book.base",
        "calibre.ebooks.metadata.sources", "calibre.ebooks.metadata.sources.base",
        "calibre.utils", "calibre.utils.date",
    )}
    modules["bs4"].BeautifulSoup = _EmptyBookPage
    modules["calibre.ebooks.metadata.book.base"].Metadata = _Metadata
    modules["calibre.ebooks.metadata.sources.base"].Source = _Source
    modules["calibre.ebooks.metadata.sources.base"].Option = lambda **kwargs: kwargs
    modules["calibre.utils.date"].strptime = lambda val, fmt: datetime.strptime(val, fmt)
    spec = importlib.util.spec_from_file_location(
        "transport_subject", Path(__file__).resolve().parents[1] / "__init__.py"
    )
    plugin = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(plugin)
    return plugin


class AuthenticatedTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plugin_type = _load_plugin().NationalLibraryOfKoreaMetadataPlugin

    def setUp(self):
        self.plugin = self.plugin_type()
        self.key = "SYNTHETIC-transport-key-000"
        self.plugin.prefs = {"api_key": self.key}
        self.book = {
            "TITLE": "Sample title", "AUTHOR": "Author One; Author Two",
            "PUBLISHER": "Sample publisher", "REAL_PUBLISH_DATE": "20251001",
            "SERIES_TITLE": "Sample series", "SERIES_NO": "2",
            "EA_ISBN": "9791190000000", "EA_ADD_CODE": "03810",
            "TITLE_URL": "https://example.invalid/cover.jpg",
        }
        self.plugin.payload = json.dumps({"docs": [self.book]}).encode()
        self.log, self.results = _Log(), Queue()

    def _callback(self, name):
        getattr(self.plugin, name)(
            self.log, self.results, Event(),
            identifiers={"isbn": "9791190000000"}, timeout=17,
        )

    def _assert_request(self):
        url, timeout, browser = self.plugin.requests[0]
        self.assertEqual(urlsplit(url).scheme, "https")
        self.assertEqual(urlsplit(url).netloc, "www.nl.go.kr")
        self.assertEqual(urlsplit(url).path, "/seoji/SearchApi.do")
        self.assertEqual(parse_qs(urlsplit(url).query), {
            "cert_key": [self.key], "result_style": ["json"], "page_no": ["1"],
            "page_size": ["1"], "isbn": ["9791190000000"],
        })
        self.assertEqual(timeout, 17)
        self.assertIsNot(browser, self.plugin._browser)
        self.assertIs(browser.context, self.plugin._browser.context)

    def test_identify_success(self):
        self._callback("identify")
        self._assert_request()
        self.assertEqual(self.results.qsize(), 1)
        metadata = self.results.get_nowait()
        self.assertEqual(metadata.title, "Sample title")
        self.assertEqual(metadata.authors, ("Author One", "Author Two"))
        self.assertEqual(metadata.identifiers, {
            "isbn": "9791190000000", "isbn_add_code": "03810",
        })
        self.assertEqual(metadata.publisher, "Sample publisher")
        self.assertEqual(metadata.pubdate, datetime(2025, 10, 1))
        self.assertEqual((metadata.series, metadata.series_index), ("Sample series", "2"))
        self.assertEqual(self.plugin.cleaned, [metadata])
        self.assertEqual(self.log.exceptions, [])

    def test_cover_success_uses_inherited_download(self):
        self._callback("download_cover")
        self._assert_request()
        self.assertEqual(self.results.qsize(), 1)
        self.assertEqual(self.results.get_nowait(), (self.plugin, b"cover bytes"))
        self.assertEqual(len(self.plugin.requests), 2)
        self.assertEqual(self.plugin.requests[1][:2], ("https://example.invalid/cover.jpg", 17))
        self.assertEqual(self.log.exceptions, [])

    def test_download_contents_and_json_success(self):
        url = self.plugin.get_book_json_url({"isbn": "9791190000000"})[2]
        self.assertEqual(self.plugin.download_contents(url, 17), self.plugin.payload)
        self.assertEqual(self.plugin.get_book_json(url, 17), self.book)
        self.assertEqual(len(self.plugin.requests), 2)

    def test_decode_json_and_empty_docs_keep_original_failure_types(self):
        for payload, error in ((b"\xff", UnicodeDecodeError),
                               (b"{", json.JSONDecodeError),
                               (b'{"docs": []}', IndexError)):
            with self.subTest(error=error):
                self.plugin.payload = payload
                url = self.plugin.get_book_json_url({"isbn": "9791190000000"})[2]
                with self.assertRaises(error):
                    self.plugin.get_book_json(url, 17)

    def test_success_logs_do_not_expose_authentication(self):
        for callback in ("identify", "download_cover"):
            with self.subTest(callback=callback):
                self.setUp()
                self._callback(callback)
                self._assert_request()
                self.assertNotIn(self.key, "\n".join(self.log.messages))
                self.assertNotIn("cert_key=", "\n".join(self.log.messages))

    def test_callback_requests_inherit_verifying_browser_policy_offline(self):
        for callback in ("identify", "download_cover"):
            with self.subTest(callback=callback):
                self.setUp()
                self._callback(callback)
                self._assert_request()
                for _, _, browser in self.plugin.requests:
                    self.assertEqual(browser.context.verify_mode, ssl.CERT_REQUIRED)
                    self.assertTrue(browser.context.check_hostname)

    def test_transport_failures_do_not_expose_authentication(self):
        for callback in ("identify", "download_cover"):
            for stage in ("open", "read"):
                for error_kind in ("http", "url", "tls", "nested"):
                    with self.subTest(callback=callback, stage=stage, error_kind=error_kind):
                        self.setUp()
                        self.plugin.failure_stage, self.plugin.error_kind = stage, error_kind
                        self._callback(callback)
                        self._assert_request()
                        self.assertTrue(self.results.empty())
                        self.assertEqual(len(self.plugin.requests), 1)
                        self.assertTrue(self.log.exceptions)
                        exception_log = "\n".join(self.log.exceptions)
                        self.assertIn("Authenticated metadata request failed", exception_log)
                        self.assertNotIn(self.key, exception_log)
                        self.assertNotIn("cert_key=", exception_log)
                        self.assertNotIn("www.nl.go.kr", exception_log)
                        self.assertNotIn(self.key, "\n".join(self.log.messages))
                        self.assertNotIn("cert_key=", "\n".join(self.log.messages))
