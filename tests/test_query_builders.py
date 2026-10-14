"""
Verify query-builder behavior with isolated Calibre import boundaries.
"""

import importlib.util
from pathlib import Path
import sys
from types import ModuleType
import unittest
from unittest.mock import patch


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


class _Identifiers:
    def __init__(self, values, events):
        self._values = iter(values)
        self._events = events

    def get(self, key):
        """
        Record each identifier lookup and supply the next observable value.
        """
        self._events.append(("get", key))
        return next(self._values)


class _QueryBuilder:
    def __init__(self, events, error=None):
        self._events = events
        self._error = error

    def get_book_json_query(self, isbn):
        """
        Record query construction after identifier reads.
        """
        self._events.append(("query", isbn))
        if self._error is not None:
            raise self._error
        return f"isbn={isbn}"


class QueryBuilderTests(unittest.TestCase):
    """
    Preserve missing-input behavior, query results and observable evaluation.
    """

    @classmethod
    def setUpClass(cls):
        """
        Load the actual plugin with host imports isolated.
        """
        cls.plugin = _load_plugin()

    def test_missing_identifiers(self):
        """
        Return no result and perform no query when identifiers are absent.
        """
        events = []
        receiver = _QueryBuilder(events)
        self.assertIsNone(self.plugin.get_isbn(None))
        self.assertIsNone(
            self.plugin.NationalLibraryOfKoreaMetadataPlugin.get_book_json_url(
                receiver, None
            )
        )
        self.assertIsNone(
            self.plugin.NationalLibraryOfKoreaMetadataPlugin.get_book_url(
                receiver, None
            )
        )
        self.assertEqual(events, [])

    def test_missing_isbn(self):
        """
        Read a missing ISBN once and return no result for each builder.
        """
        for builder in (
            self.plugin.get_isbn,
            lambda identifiers: (
                self.plugin.NationalLibraryOfKoreaMetadataPlugin.get_book_json_url(
                    _QueryBuilder(events), identifiers
                )
            ),
            lambda identifiers: (
                self.plugin.NationalLibraryOfKoreaMetadataPlugin.get_book_url(
                    _QueryBuilder(events), identifiers
                )
            ),
        ):
            with self.subTest(builder=builder):
                events = []
                self.assertIsNone(builder(_Identifiers([None], events)))
                self.assertEqual(events, [("get", "isbn")])

    def test_isbn_split_and_read_order(self):
        """
        Split the actual second read without replacing it with the guard read.
        """
        for value in ("9791190000000 (paperback)", "9791190000000 extra"):
            with self.subTest(value=value):
                events = []
                result = self.plugin.get_isbn(_Identifiers(["guard", value], events))
                self.assertEqual(result, "9791190000000")
                self.assertEqual(events, [("get", "isbn"), ("get", "isbn")])

    def test_json_url_evaluation_order(self):
        """
        Construct the query once after all three original identifier reads.
        """
        events = []
        identifiers = _Identifiers(["outer", "inner", "9791190000000 extra"], events)
        result = self.plugin.NationalLibraryOfKoreaMetadataPlugin.get_book_json_url(
            _QueryBuilder(events), identifiers
        )
        self.assertEqual(
            result,
            (
                "isbn",
                "9791190000000",
                "https://www.nl.go.kr/seoji/SearchApi.do?isbn=9791190000000",
            ),
        )
        self.assertEqual(
            events,
            [("get", "isbn"), ("get", "isbn"), ("get", "isbn"),
             ("query", "9791190000000")],
        )

    def test_detail_url_evaluation_order(self):
        """
        Build the detail URL from the third read with its exact query fields.
        """
        events = []
        identifiers = _Identifiers(["outer", "inner", "9791190000000 extra"], events)
        result = self.plugin.NationalLibraryOfKoreaMetadataPlugin.get_book_url(
            _QueryBuilder(events), identifiers
        )
        self.assertEqual(
            result,
            (
                "isbn",
                "9791190000000",
                "https://nl.go.kr/seoji/contents/S80100000000.do"
                "?schM=intgr_detail_view_isbn&isbn=9791190000000",
            ),
        )
        self.assertEqual(events, [("get", "isbn"), ("get", "isbn"), ("get", "isbn")])

    def test_empty_isbn_is_preserved(self):
        """
        Preserve empty-string results rather than treating them as absent.
        """
        self.assertEqual(self.plugin.get_isbn({"isbn": ""}), "")
        self.assertEqual(
            self.plugin.NationalLibraryOfKoreaMetadataPlugin.get_book_json_url(
                _QueryBuilder([]), {"isbn": ""}
            ),
            ("isbn", "", "https://www.nl.go.kr/seoji/SearchApi.do?isbn="),
        )
        self.assertEqual(
            self.plugin.NationalLibraryOfKoreaMetadataPlugin.get_book_url(
                _QueryBuilder([]), {"isbn": ""}
            ),
            (
                "isbn", "", "https://nl.go.kr/seoji/contents/S80100000000.do"
                "?schM=intgr_detail_view_isbn&isbn=",
            ),
        )

    def test_inner_missing_isbn_failures(self):
        """
        Keep the distinct JSON-query and detail-query handling of a later None.
        """
        events = []
        result = self.plugin.NationalLibraryOfKoreaMetadataPlugin.get_book_json_url(
            _QueryBuilder(events), _Identifiers(["outer", None], events)
        )
        self.assertEqual(
            result, ("isbn", None, "https://www.nl.go.kr/seoji/SearchApi.do?isbn=None")
        )
        self.assertEqual(events, [("get", "isbn"), ("get", "isbn"), ("query", None)])
        events = []
        with self.assertRaises(TypeError):
            self.plugin.NationalLibraryOfKoreaMetadataPlugin.get_book_url(
                _QueryBuilder(events), _Identifiers(["outer", None], events)
            )
        self.assertEqual(events, [("get", "isbn"), ("get", "isbn")])

    def test_identifier_failure_propagation(self):
        """
        Propagate lookup failures at the original read without constructing a query.
        """
        events = []
        with self.assertRaises(StopIteration):
            self.plugin.get_isbn(_Identifiers(["guard"], events))
        self.assertEqual(events, [("get", "isbn"), ("get", "isbn")])
        for builder in (
            self.plugin.NationalLibraryOfKoreaMetadataPlugin.get_book_json_url,
            self.plugin.NationalLibraryOfKoreaMetadataPlugin.get_book_url,
        ):
            with self.subTest(builder=builder):
                events = []
                with self.assertRaises(StopIteration):
                    builder(_QueryBuilder(events), _Identifiers(["outer", "inner"], events))
                self.assertEqual(
                    events, [("get", "isbn"), ("get", "isbn"), ("get", "isbn")]
                )

    def test_query_failure_propagation(self):
        """
        Propagate the original query error after its single construction attempt.
        """
        events = []
        error = ValueError("query rejected")
        with self.assertRaises(ValueError) as caught:
            self.plugin.NationalLibraryOfKoreaMetadataPlugin.get_book_json_url(
                _QueryBuilder(events, error), {"isbn": "9791190000000"}
            )
        self.assertIs(caught.exception, error)
        self.assertEqual(events, [("query", "9791190000000")])
