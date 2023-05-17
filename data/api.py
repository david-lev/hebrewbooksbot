import json
from typing import Callable
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


def _make_request(
        endpoint: str,
        params: dict[str, str | int] | None = None,
        convert_to: str | None = None
) -> dict | list | str:
    """
    Make a request to HebrewBooks.org

    Args:
        endpoint: The endpoint to send the request to (e.g. '/search')
        params: The parameters to send (e.g. {'searchtype': 'all', 'search': 'אבגדה'})
        convert_to: The type to convert the response to (either 'dict', 'list' or 'html')
    """
    print("Making request...")
    res = requests.get(f'{BASE_API}{endpoint}', params=params)
    res.raise_for_status()
    start, end = ('[', ']') if convert_to == 'list' else ('{', '}')
    return json.loads(res.text[res.text.index(start):res.text.rindex(end) + 1]) \
        if convert_to not in ('html', None) else res.text if convert_to == 'html' else res.json()


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
        params={'json': 1, 'autosuggest': 1, 'limit': limit, 'src': search_type, 'q': query},
        convert_to=None
    )


@lru_cache
def get_masechtot() -> list[Masechet]:
    """
    Get all masechtot from HebrewBooks.org
    """
    html = _make_request(
        endpoint='/shas.aspx',
        convert_to='html'
    )
    return [
        Masechet(id=int(m['value']), name=m.text)
        for m in BeautifulSoup(html, 'html.parser').find('select', {'id': 'cpMstr_ddlMesechtas'}).find_all('option')
    ]


@lru_cache
def get_masehet(masehet: Masechet) -> Masechet:
    """
    Get a masechet from HebrewBooks.org

    Args:
        masehet: The masechet to get
    """
    html = _make_request(
        endpoint=f'/shas.aspx',
        params={'mesechta': masehet.id},
        convert_to='html'
    )
    soup = BeautifulSoup(html, 'html.parser')
    book_id = int(soup.find('div', {'id': 'shaspngcont'}).get('rel').split('_')[0])
    return Masechet(
        id=masehet.id,
        name=masehet.name,
        pages=[
            MasechetPage(id=p['value'], masechet_id=masehet.id, name=p.text, book_id=book_id)
            for p in soup.find('select', {'id': 'cpMstr_ddlDafim'}).find_all('option')
        ]
    )


def _get_sections(
        soup: BeautifulSoup,
        soup_func: Callable[[BeautifulSoup], ResultSet[PageElement]],
        title_funcs: tuple[Callable[[PageElement], str], ...],
        content_funcs: tuple[Callable[[PageElement], str], ...],
        sep: str = ' '
) -> list[Section]:
    """
    Get a section from a BeautifulSoup object

    Args:
        soup: The BeautifulSoup object
        soup_func: The function to get the page element
        title_funcs: The functions to get the title
        content_funcs: The functions to get the content
        sep: The separator to use when joining the results
    Returns:
        list[Section]: The sections
    """
    page_element = soup_func(soup)
    sections = []
    for span in page_element:
        try:
            sections.append(
                Section(
                    title=sep.join([func(span).strip() for func in title_funcs]),
                    content=sep.join([func(span).strip() for func in content_funcs])
                )
            )
        except AttributeError:
            print("failed to parse section")

    return sections


@lru_cache
def get_page(page: MasechetPage) -> MasechetPage:
    """
    Get a masechet page from HebrewBooks.org

    Args:
        page: The page to get
    """
    html = _make_request(
        endpoint=f'/shas.aspx',
        params={'mesechta': page.masechet_id, 'daf': page.id, 'format': 'text'},
        convert_to='html'
    )
    soup = BeautifulSoup(html, 'html.parser')
    return MasechetPage(
        id=page.id,
        masechet_id=page.masechet_id,
        book_id=page.book_id,
        name=page.name,
        content=PageContent(
            gmara=_get_sections(
                soup=soup,
                soup_func=lambda sp: sp.find('div', class_='shastext2').find_all('span'),
                title_funcs=(lambda spn: spn.text,),
                content_funcs=(lambda spn: spn.next_sibling if spn.next_sibling else '',)
            ),
            rashi=_get_sections(
                soup=soup,
                soup_func=lambda sp: sp.find('div', class_='shastext3').find_all('span', class_='five'),
                title_funcs=(lambda spn: spn.text,),
                content_funcs=(lambda spn: str(spn.next_sibling if spn.next_sibling else ''),)
            ) if soup.find('div', class_='shastext3') else None,
            tosfot=_get_sections(
                soup=soup,
                soup_func=lambda sp: sp.find('div', class_='shastext4').find_all('div'),
                title_funcs=(
                    lambda spn: spn.find('span', class_='shastitle7').text,
                    lambda spn: spn.find('span', class_='five').text,
                ),
                content_funcs=(lambda spn: str(spn.find('span', class_='five').next_sibling),)
            ) if soup.find('div', class_='shastext4') else None
        )
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
    masechtot = get_masechtot()
    assert len(masechtot) == 37
    masehet = get_masehet(masechtot[0])
    assert masehet.id == masechtot[0].id
    assert get_page(masehet.pages[0]).id == masehet.pages[0].id
