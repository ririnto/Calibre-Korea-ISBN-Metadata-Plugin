"""
Verify query-builder behavior with isolated Calibre import boundaries.
"""

import importlib.util
from itertools import product
from pathlib import Path
import sys
from types import ModuleType
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit


class _HostOption:
    def __init__(self, **attributes):
        self.__dict__.update(attributes)


def _load_plugin():
    modules = {
        name: ModuleType(name)
        for name in (
            "bs4",
            "calibre",
            "calibre.ebooks",
            "calibre.ebooks.metadata",
            "calibre.ebooks.metadata.book",
            "calibre.ebooks.metadata.book.base",
            "calibre.ebooks.metadata.sources",
            "calibre.ebooks.metadata.sources.base",
            "calibre.utils",
            "calibre.utils.date",
        )
    }
    modules["calibre.ebooks.metadata.book.base"].Metadata = object
    modules["calibre.ebooks.metadata.sources.base"].Source = object
    modules["calibre.ebooks.metadata.sources.base"].Option = _HostOption
    modules["calibre.utils.date"].strptime = object
    spec = importlib.util.spec_from_file_location(
        "query_builder_subject", Path(__file__).resolve().parents[1] / "__init__.py"
    )
    plugin = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(plugin)
    return plugin


class QueryBuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = _load_plugin()

    def setUp(self):
        self.plugin = self.module.NationalLibraryOfKoreaMetadataPlugin()
        self.plugin.prefs = {"api_key": "SYNTHETIC-query-key"}

    def test_missing_identifiers(self):
        self.assertIsNone(self.module.get_isbn(None))
        self.assertIsNone(self.plugin.get_book_json_url(None))
        self.assertIsNone(self.plugin.get_book_url(None))

    def test_missing_isbn(self):
        identifiers = {"isbn": None}
        self.assertIsNone(self.module.get_isbn(identifiers))
        self.assertIsNone(self.plugin.get_book_json_url(identifiers))
        self.assertIsNone(self.plugin.get_book_url(identifiers))

    def test_generated_isbn_suffixes_keep_both_lookup_urls_consistent(self):
        """
        Keep the ISBN before the first space or parenthesis in both URLs.
        """
        for prefix, separator, suffix in product(
            ("", "0", "9791190000000", "978123456789X"),
            (" ", "("),
            ("", "paperback", " extra (volume 2)"),
        ):
            with self.subTest(prefix=prefix, separator=separator, suffix=suffix):
                identifiers = {"isbn": prefix + separator + suffix}
                self.assertEqual(self.module.get_isbn(identifiers), prefix)
                for builder in (self.plugin.get_book_json_url, self.plugin.get_book_url):
                    kind, isbn, url = builder(identifiers)
                    self.assertEqual((kind, isbn), ("isbn", prefix))
                    self.assertEqual(
                        parse_qs(urlsplit(url).query, keep_blank_values=True).get("isbn"),
                        [prefix],
                    )

    def test_detail_url(self):
        for expected_isbn in ("9791190000000", "9791190000000+&=%#"):
            with self.subTest(expected_isbn=expected_isbn):
                kind, isbn, url = self.plugin.get_book_url({"isbn": expected_isbn + " extra"})
                self.assertEqual((kind, isbn), ("isbn", expected_isbn))
                parsed = urlsplit(url)
                self.assertEqual(
                    (parsed.scheme, parsed.netloc, parsed.path),
                    ("https", "nl.go.kr", "/seoji/contents/S80100000000.do"),
                )
                self.assertEqual(
                    parse_qs(parsed.query),
                    {"schM": ["intgr_detail_view_isbn"], "isbn": [expected_isbn]},
                )

    def test_authenticated_lookup_query(self):
        for key, expected_isbn in (
            ("SYNTHETIC-query-key", "9791190000000"),
            ("SYNTHETIC-key +/&=%#", "9791190000000+&=%#"),
            ("", ""),
        ):
            with self.subTest(key=key, expected_isbn=expected_isbn):
                self.plugin.prefs = {"api_key": key}
                kind, isbn, url = self.plugin.get_book_json_url({"isbn": expected_isbn})
                self.assertEqual((kind, isbn), ("isbn", expected_isbn))
                self.assertEqual(
                    parse_qs(urlsplit(url).query, keep_blank_values=True),
                    {
                        "cert_key": [key],
                        "result_style": ["json"],
                        "page_no": ["1"],
                        "page_size": ["1"],
                        "isbn": [expected_isbn],
                    },
                )

    def test_authenticated_lookup_rejects_unset_key(self):
        self.plugin.prefs = {"api_key": None}
        with self.assertRaises(TypeError):
            self.plugin.get_book_json_url({"isbn": "9791190000000"})

    def test_empty_isbn_is_preserved(self):
        identifiers = {"isbn": ""}
        self.assertEqual(self.module.get_isbn(identifiers), "")
        for builder in (self.plugin.get_book_json_url, self.plugin.get_book_url):
            with self.subTest(builder=builder.__name__):
                kind, isbn, url = builder(identifiers)
                self.assertEqual((kind, isbn), ("isbn", ""))
                self.assertEqual(
                    parse_qs(urlsplit(url).query, keep_blank_values=True).get("isbn"), [""]
                )
