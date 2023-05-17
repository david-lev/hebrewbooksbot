import json
import requests
from functools import lru_cache
from data.enums import BrowseType
from data.models import Letter, DateRange, Subject, Book, SearchResults, Masechet, MasechetPage, PageContent, Section
from bs4 import BeautifulSoup, ResultSet, PageElement

BASE_API = 'https://beta.hebrewbooks.org'


def js_to_py(data: str, to: str) -> dict | list:
    """Convert JavaScript to Python"""
    start, end = ('[', ']') if to == 'list' else ('{', '}')
    return json.loads(data[data.index(start):data.rindex(end) + 1])


def _make_request(endpoint: str, params: dict[str, str], convert_to: str | None) -> dict | list:
    """
    Make a request to HebrewBooks.org

    Args:
        endpoint: The endpoint to send the request to (e.g. '/search')
        params: The parameters to send (e.g. {'searchtype': 'all', 'search': 'אבגדה'})
        convert_to: The type to convert the response to (either 'dict' or 'list')
    """
    res = requests.get(f'{BASE_API}{endpoint}', params=params)
    res.raise_for_status()
    start, end = ('[', ']') if convert_to == 'list' else ('{', '}')
    return json.loads(res.text[res.text.index(start):res.text.rindex(end) + 1]) if convert_to else res.json()


@lru_cache
def get_letters() -> list[Letter]:
    """Get all letters from HebrewBooks.org"""
    data = _make_request(
        endpoint='/api/api.ashx',
        params={'req': 'subject_list', 'type': 'letter', 'callback': 'bot'},
        convert_to='list'
    )
    return [Letter(**letter) for letter in data]


@lru_cache
def get_date_ranges() -> list[DateRange]:
    """Get all date ranges from HebrewBooks.org"""
    data = _make_request(
        endpoint='/api/api.ashx',
        params={'req': 'subject_list', 'type': 'daterange', 'callback': 'bot'},
        convert_to='list'
    )
    return [DateRange(**date_range) for date_range in data]


@lru_cache
def get_subjects() -> list[Subject]:
    """Get all subjects from HebrewBooks.org"""
    data = _make_request(
        endpoint='/api/api.ashx',
        params={'req': 'subject_list', 'type': 'subject', 'callback': 'bot'},
        convert_to='list'
    )
    return [Subject(**subject) for subject in data]


@lru_cache
def get_book(book_id: int) -> Book | None:
    """
    Get book information from HebrewBooks.org

    Args:
        book_id: The book's ID

    Returns:
        Book: The book's information
    """
    try:
        return Book(**_make_request(
            endpoint='/api/api.ashx',
            params={'req': 'book_info', 'id': book_id, 'callback': 'bot'},
            convert_to='dict'
        ))
    except requests.HTTPError as e:
        if e.response.status_code == 400:
            return None
        raise


@lru_cache(maxsize=10_000)
def search(title: str, author: str, offset: int, limit: int) -> tuple[list[SearchResults], int]:
    """
    Search for books on HebrewBooks.org

    Args:
        title: The book's title
        author: The book's author
        offset: The offset to start from
        limit: The number of results to return
    Returns:
        tuple[list[SearchResults], int]: The search results and the total number of results
    """
    if not any((title, author)):
        raise ValueError('You must specify a title or author')
    try:
        data = _make_request(
            endpoint='/api/api.ashx',
            params={'author_search': author, 'title_search': title, 'start': offset, 'length': limit, 'callback': 'bot'},
            convert_to='dict'
        )
    except ValueError:
        return [], 0
    return [SearchResults(**b) for b in data['data']], data['total']


@lru_cache(maxsize=10_000)
def browse(browse_type: BrowseType, browse_id: int | str, offset: int, limit: int) -> tuple[list[SearchResults], int]:
    """
    Browse books on HebrewBooks.org

    Args:
        browse_type: The type of search
        browse_id: The ID of the search
        offset: The offset to start from
        limit: The number of results to return
    Returns:
        tuple[list[SearchResults], int]: The search results and the total number of results
    """
    data = _make_request(
        endpoint='/api/api.ashx',
        params={'req': 'title_list_for_subject', 'list_type': browse_type.value, 'id': browse_id,
                'start': offset, 'length': limit, 'callback': 'bot'},
        convert_to='dict'
    )
    return [SearchResults(**book) for book in data['data']], data['total']


@lru_cache(maxsize=10_000)
def get_suggestions(query: str, search_type: str, limit: int) -> list[str]:
    """
    Get suggestions for a search on HebrewBooks.org

    Args:
        query: The query to search for
        search_type: The type of search
        limit: The number of results to return
    Returns:
        list[str]: The search results
    """
    if search_type not in ('title', 'auth', 'ocr'):
        raise ValueError('Invalid type')
    return _make_request(
        endpoint='/suggest/suggest.ashx',
        params={'json': 1, 'autosuggest': 1,  'limit': limit, 'src': search_type, 'q': query},
        convert_to=None
    )


if __name__ == '__main__':
    letters = get_letters()
    assert len(browse(BrowseType.LETTER, letters[0].id, offset=1, limit=5)[0]) == 5
    subjects = get_subjects()
    assert len(browse(BrowseType.SUBJECT, subjects[0].id, offset=1, limit=5)[0]) == 5
    daterange = get_date_ranges()
    assert len(browse(BrowseType.DATERANGE, daterange[0].id, offset=1, limit=5)[0]) == 5
    search_res, total = search(title="דוד", author='דוד', offset=1, limit=10)
    assert get_book(search_res[0].id).id == search_res[0].id
    assert len(search_res) == 10
    assert all(('דוד' in res.title for res in search_res))
    assert search(title='123456789', author='', offset=1, limit=5) == ([], 0)
    assert len(get_suggestions(query='דוד', search_type='title', limit=10)) == 10

