import csv
from typing import Callable
from bs4 import BeautifulSoup, ResultSet, PageElement
from data.models import Section
from data.strings import String, STRINGS


def get_sections(
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


def get_title_author(text: str) -> tuple[str, str]:
    """
    Get the title and author from a text.
    """
    return (t.strip() for t in text.split(':', 1)) if ':' in text else (text.strip(), '')


def get_offset(current_offset: int, total: int, increase: int = 5) -> int:
    """
    Get the offset for thr next query results.

    Args:
        current_offset: The current offset.
        total: The total number of results.
        increase: The number of results to increase. (default: 5)
    Returns:
        The offset for the next query results (0 if there are no more results).
    """
    if (current_offset + increase) > total:
        offset = total - current_offset
        return 0 if offset < increase else offset
    return current_offset + increase


def write_strings_to_csv(filename: str):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Key', 'Language', 'Translation'])
        for key, translations_dict in STRINGS.items():
            for lang, translation in translations_dict.items():
                writer.writerow([key.name, lang, translation])


if __name__ == '__main__':
    import sys
    write_strings_to_csv(sys.argv[1])
