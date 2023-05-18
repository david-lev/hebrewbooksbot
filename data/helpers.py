from typing import Callable
from bs4 import BeautifulSoup, ResultSet, PageElement
from data.models import Section


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

