import json
import requests
from functools import lru_cache
from data.models import Letter, DateRange, Subject, Book, SearchResults

BASE_API = 'https://beta.hebrewbooks.org/api/api.ashx'


def js_to_py(data: str, to: str) -> dict | list:
    """Convert JavaScript to Python"""
    start, end = ('[', ']') if to == 'list' else ('{', '}')
    return json.loads(data[data.index(start):data.rindex(end) + 1])


def _make_request(prams: dict[str, str], convert_to: str) -> dict | list:
    """
    Make a request to HebrewBooks.org

    Args:
        prams: The parameters to send (e.g. {'req': 'search', 'searchtype': 'all', 'search': 'אבגדה'})
        convert_to: The type to convert the response to (either 'dict' or 'list')
    """
    res = requests.get(f'{BASE_API}?callback=bot', params=prams)
    print(res.url)
    res.raise_for_status()
    start, end = ('[', ']') if convert_to == 'list' else ('{', '}')
    return json.loads(res.text[res.text.index(start):res.text.rindex(end) + 1])


@lru_cache
def get_letters() -> list[Letter]:
    """Get all letters from HebrewBooks.org"""
    data = _make_request({'req': 'subject_list', 'type': 'letter'}, convert_to='list')
    return [Letter(**letter) for letter in data]


@lru_cache
def get_date_ranges() -> list[DateRange]:
    """Get all date ranges from HebrewBooks.org"""
    data = _make_request({'req': 'subject_list', 'type': 'daterange'}, convert_to='list')
    return [DateRange(**date_range) for date_range in data]


@lru_cache
def get_subjects() -> list[Subject]:
    """Get all subjects from HebrewBooks.org"""
    data = _make_request({'req': 'subject_list', 'type': 'subject'}, convert_to='list')
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
        return Book(**_make_request({'req': 'book_info', 'id': book_id}, convert_to='dict'))
    except requests.HTTPError as e:
        if e.response.status_code == 400:
            return None
        raise


@lru_cache(maxsize=10_000)
def search(title: str = '', author: str = '', offset: int = 1, limit: int = 30) -> tuple[list[SearchResults], int]:
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
        data = _make_request({'author_search': author, 'title_search': title, 'start': offset, 'length': limit},
                             convert_to='dict')
    except ValueError:
        return [], 0
    return [SearchResults(**b) for b in data['data']], data['total']


@lru_cache(maxsize=10_000)
def browse(_type: str, _id: int | str, offset: int = 1, limit: int = 30) -> tuple[list[SearchResults], int]:
    """
    Browse books on HebrewBooks.org

    Args:
        _type: The type of search
        _id: The ID of the search
        offset: The offset to start from
        limit: The number of results to return
    Returns:
        tuple[list[SearchResults], int]: The search results and the total number of results
    """
    if _type not in ('letter', 'daterange', 'subject'):
        raise ValueError('Invalid type')
    data = _make_request({'req': 'title_list_for_subject', 'list_type': _type, 'id': _id,
                          'start': offset, 'length': limit}, convert_to='dict')
    return [SearchResults(**book) for book in data['data']], data['total']


if __name__ == '__main__':
    letters = get_letters()
    assert len(browse('letter', letters[0].id, offset=1, limit=5)[0]) == 5
    subjects = get_subjects()
    assert len(browse('subject', subjects[0].id, offset=1, limit=5)[0]) == 5
    daterange = get_date_ranges()
    assert len(browse('daterange', daterange[0].id, offset=1, limit=5)[0]) == 5
    search_res, total = search(title="דוד", author='דוד', offset=1, limit=10)
    assert get_book(search_res[0].id).id == search_res[0].id
    assert len(search_res) == 10
    assert all(('דוד' in res.title for res in search_res))
    assert search(title='123456789') == ([], 0)
