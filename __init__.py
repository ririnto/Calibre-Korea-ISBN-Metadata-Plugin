import json
import re

import bs4

from calibre.ebooks.metadata.book.base import Metadata
from calibre.ebooks.metadata.sources.base import Source, Option
from calibre.utils.date import strptime


def remove_empty_strings(items):
    """
    @param items: Iterable[str]
    @return: tuple[str]
    """
    return tuple(filter(lambda item: item, items))


def filter_not_include(items, keywords):
    """
    @param items: Iterable[str]
    @param keywords: Iterable[str]
    @return: tuple[str]
    """
    return tuple(filter(lambda item: all(keyword not in item for keyword in keywords), items))


def remove_keywords_in_string(item, keywords):
    """
    @param item: str
    @param keywords: Iterable[str]
    @return: str
    """
    for keyword in keywords:
        item = item.replace(keyword, "")

    return item


def remove_keywords_in_strings(items, keywords):
    """
    @param items: Iterable[str]
    @param keywords: Iterable[str]
    @return: Iterable[str]
    """
    return tuple(map(lambda item: remove_keywords_in_string(item=item, keywords=keywords), items))


def trim_whitespaces_in_strings(items):
    """
    @param items: Iterable[str]
    @return: Iterable[str]
    """
    return tuple(map(lambda item: item.strip(), items))


def get_isbn(identifiers):
    """
    @param identifiers: Optional[dict[str, str]]
    @return: Optional[str]
    """
    if identifiers is None or identifiers.get("isbn") is None:
        return None

    return re.split(pattern='[( ]', string=identifiers.get("isbn"))[0]


def get_book_query(isbn):
    """
    @param isbn: str
    @return: str
    """
    return '&'.join(('='.join(("schM", "intgr_detail_view_isbn")), '='.join(("isbn", isbn))))


class NationalLibraryOfKoreaMetadataPlugin(Source):
    name: str = "Korea ISBN Metadata Plugin"
    author: str = "rinto.ri"
    version: tuple[int, int, int] = (1, 0, 0)
    minimum_calibre_version: tuple[int, int, int] = (7, 0, 0)
    description: str = "National Library of Korea Metadata Plugin"
    supported_platforms: list[str] = ["windows", "osx", "linux"]
    capabilities: frozenset[str] = frozenset(("identify", "cover"))
    touched_fields: frozenset[str] = frozenset((
        "title",
        "authors",
        "identifier:doi",
        "identifier:isbn",
        "identifier:isbn_add_code",
        "publisher",
        "series",
        "pubdate",
        "languages",
        "comments",
        "tags"
    ))
    options: tuple[Option] = (Option(name="api_key", type_="string", default=None, label="api_key", desc="api_key"),)
    prefer_results_with_isbn: bool = True
    ignore_ssl_errors: bool = True
    has_html_comments: bool = True

    def is_configured(self):
        """
        @return: bool
        """
        return self.prefs.get('api_key')

    def identify(self, log, result_queue, abort, title=None, authors=None, identifiers=None, timeout=30):
        """
        @param log: Log
        @param result_queue: Queue
        @param abort: Event
        @param title: Optional[str]
        @param authors: Optional[list[str]]
        @param identifiers: Optional[dict[str, str]]
        @param timeout: int
        """
        if identifiers is None:
            identifiers = {}
        log.info(f"identify - start. title={title}, authors={authors}, identifiers={identifiers}")

        try:
            book_json_url: str = self.get_book_json_url(identifiers=identifiers)[2]
            log.debug(book_json_url)

            book_json = self.get_book_json(url=book_json_url, timeout=timeout)
            log.debug(book_json)

            title = book_json.get("TITLE")
            if book_json.get("AUTHOR"):
                authors = remove_empty_strings(
                    items=trim_whitespaces_in_strings(
                        items=remove_keywords_in_strings(
                            items=filter_not_include(
                                items=re.split(pattern='[/,;]', string=book_json.get("AUTHOR")),
                                keywords=("옮김", "엮은이", "역자")
                            ),
                            keywords=("지은이", ":", "저자", "작가", "지음")
                        )
                    )
                )
            else:
                authors = None

            mi = Metadata(title=title, authors=authors)
            mi.publisher = book_json.get("PUBLISHER")

            try:
                if book_json.get("REAL_PUBLISH_DATE") or book_json.get("PUBLISH_PREDATE"):
                    pubdate = book_json.get("REAL_PUBLISH_DATE") or book_json.get("PUBLISH_PREDATE")
                    mi.pubdate = strptime(val=pubdate, fmt="%Y%m%d")
            except Exception as e:
                log.exception(e)

            mi.series = book_json.get("SERIES_TITLE")
            mi.series_index = book_json.get("SERIES_NO")

            mi.set_identifier(typ="isbn", val=book_json.get("EA_ISBN"))
            mi.set_identifier(typ="isbn_add_code", val=book_json.get("EA_ADD_CODE"))

            try:
                book_url = self.get_book_url(identifiers=identifiers)
                log.debug(book_url)

                if book_url is None:
                    raise "book_url is None"

                book_info = self.get_book_info(url=book_url[2], timeout=timeout)
                log.debug(book_info)

                try:
                    if book_info.get("키워드"):
                        mi.tags = remove_empty_strings(
                            items=trim_whitespaces_in_strings(
                                items=remove_keywords_in_strings(
                                    items=re.split(pattern='[,;]', string=book_info.get("키워드")),
                                    keywords=("TAG", ":")
                                )
                            )
                        )
                except Exception as e:
                    log.exception(e)

                try:
                    if book_info.get("DOI"):
                        mi.set_identifier(typ="doi", val=book_info.get("DOI").lstrip("https://doi.org/"))
                except Exception as e:
                    log.exception(e)

                try:
                    if book_info.get("형태 및 본문언어") or book_info.get("서비스형태 및 본문언어"):
                        mi.languages = (
                            (book_info.get("형태 및 본문언어") or book_info.get("서비스형태 및 본문언어")).split('/')[-1].strip(),
                        )
                except Exception as e:
                    log.exception(e)

                try:
                    if book_info.get("comments"):
                        mi.comments = book_info.get("comments")
                except Exception as e:
                    log.exception(e)
            except Exception as e:
                log.exception(e)

            self.clean_downloaded_metadata(mi=mi)

            log.debug(mi)

            result_queue.put(mi)
        except Exception as e:
            log.exception(e)

    def download_cover(
            self,
            log,
            result_queue,
            abort,
            title=None,
            authors=None,
            identifiers=None,
            timeout=30,
            get_best_cover=False
    ):
        """
        @param log: Log
        @param result_queue: Queue
        @param abort: Event
        @param title: Optional[str]
        @param authors: Optional[list[str]]
        @param identifiers: Optional[dict[str, str]]
        @param timeout: int
        @param get_best_cover: bool
        """
        if identifiers is None:
            identifiers = {}
        book_url = self.get_book_json_url(identifiers=identifiers)[2]
        log.debug(book_url)

        book_json = self.get_book_json(url=book_url, timeout=timeout)
        log.debug(book_json)

        self.download_image(url=book_json.get("TITLE_URL"), timeout=timeout, log=log, result_queue=result_queue)

    def download_contents(self, url, timeout):
        """
        @param url: str
        @param timeout: int
        @return: bytes
        """
        return self.browser.open_novisit(url_or_request=url, timeout=timeout).read()

    def get_book_info(self, url, timeout):
        """
        @type url: str
        @type timeout: int
        @return dict[str, str]
        """
        contents = self.download_contents(url=url, timeout=timeout).decode()
        root = bs4.BeautifulSoup(markup=contents, features="html.parser")
        lis = root.select(
            selector="#contents > div > div.resultViewDetail > div.resultBookInfo > div.bookDataWrap > ul > li"
        )

        data = {li.select_one(selector="strong").text.strip(): li.select_one(selector="div").text.strip() for li in lis}
        if "책소개" in root.text and root.select_one(".searchViewInfo"):
            data["comments"] = root.select_one(".searchViewInfo").decode()

        return data

    def get_book_json_url(self, identifiers):
        """
        @param identifiers: Optional[dict[str, str]]
        @return: Optional[tuple[str, str, str]]
        """
        if identifiers is None or identifiers.get("isbn") is None:
            return None

        isbn = get_isbn(identifiers=identifiers)

        return "isbn", isbn, f"https://www.nl.go.kr/seoji/SearchApi.do?{self.get_book_json_query(isbn=isbn)}"

    def get_book_url(self, identifiers):
        """
        @param identifiers: Optional[dict[str, str]]
        @return: Optional[tuple[str, str, str]]
        """
        if identifiers is None or identifiers.get("isbn") is None:
            return None

        isbn = get_isbn(identifiers=identifiers)

        return "isbn", isbn, f"https://nl.go.kr/seoji/contents/S80100000000.do?{get_book_query(isbn=isbn)}"

    def get_book_json_query(self, isbn):
        """
        @param isbn: str
        @return: str
        """
        return '&'.join((
            '='.join(("cert_key", self.prefs.get('api_key'))),
            '='.join(("result_style", "json")),
            '='.join(("page_no", '1')),
            '='.join(("page_size", '1')),
            '='.join(("isbn", isbn))
        ))

    def get_book_json(self, url, timeout):
        """
        @param url: str
        @param timeout: int
        @return: dict[str, str]
        """
        contents = self.download_contents(url=url, timeout=timeout).decode()

        return json.loads(contents).get("docs")[0]
