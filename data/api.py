from functools import lru_cache
import requests
from data.models import Letter, DateRange, Subject, Book, SearchResults
from data import utils

BASE_API = 'https://beta.hebrewbooks.org/api/api.ashx'


def get_letters() -> list[Letter]:
    """Get all letters from HebrewBooks.org"""
    data = requests.get(f'{BASE_API}?req=subject_list&type=letter&callback=setSubjects').text
    return [Letter(**letter) for letter in utils.js_to_py(data)]


def get_date_ranges() -> list[DateRange]:
    """Get all date ranges from HebrewBooks.org"""
    data = requests.get(f'{BASE_API}?req=subject_list&type=daterange&callback=setSubjects').text
    return [DateRange(**date_range) for date_range in utils.js_to_py(data)]


def get_subjects() -> list[Subject]:
    """Get all subjects from HebrewBooks.org"""
    data = requests.get(f'{BASE_API}?req=subject_list&type=subject&callback=setSubjects').text
    return [Subject(**subject) for subject in utils.js_to_py(data)]


@lru_cache
def get_book(book_id: int) -> Book:
    """
    Get book information from HebrewBooks.org

    Args:
        book_id: The book's ID

    Returns:
        Book: The book's information
    """
    data = requests.get(f'{BASE_API}?req=book_info&id={book_id}&callback=setBookInfo').text
    return Book(**utils.js_to_py(data, to='dict'))


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
    res = requests.get(f'{BASE_API}?author_search={title}&title_search={author}'
                       f'&start={offset}&length={limit}&callback=setTitleAuthorSearch').text
    data = utils.js_to_py(res, to='dict')
    return [SearchResults(**b) for b in data['data']], data['total']


def browse(_type: str, _id: int | str, offset: int = 1, limit: int = 30) -> list[SearchResults]:
    """
    Browse books on HebrewBooks.org

    Args:
        _type: The type of search
        _id: The ID of the search
        offset: The offset to start from
        limit: The number of results to return
    Returns:
        list[SearchResults]: The search results
    """
    if _type not in ('letter', 'daterange', 'subject'):
        raise ValueError('Invalid type')
    res = requests.get(f'{BASE_API}?req=title_list_for_subject&list_type={_type}&id={_id}'
                       f'&start={offset}&length={limit}&callback=setSubjectTitles').text
    return [SearchResults(**book) for book in utils.js_to_py(res, to='dict')['data']]
