from enum import Enum
from functools import lru_cache
from typing import Callable, Any
from pyrogram.types import Message, CallbackQuery
from data import api
from data.models import Book
from data.enums import BrowseType as BrowseTypeEnum
from tg.callbacks import CallbackData, JumpToPage
from tg.strings import String as s

RTL = '\u200f'
LTR = '\u200e'


class Menu:
    START = 'start'
    BROWSE = 'browse_menu'
    STATS = 'start_stats'
    GITHUB_URL = 'https://github.com/david-lev/hebrewbooksbot'
    HEBREWBOOKS_SITE_URL = 'https://hebrewbooks.org'


def get_book_text(book: Book, page: int | None = None) -> str:
    """
    Get the text for a book.

    Args:
        book: The book.
        page: If provided, the page url will be added to the text, else the pdf url will be added.
    """
    return "".join((
        f"{RTL}[📚]({book.pdf_url if page is None else book.get_page_img(page, width=2138, height=3038)}) {book.title}\n",
        f"{RTL}👤 {book.author}\n",
        f"{RTL}📅 {book.year}\n" if book.year else "",
        f"{RTL}🏙 {book.city}\n" if book.city else "",
        f"{RTL}📖 {book.pages}\n",
    ))


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


def jump_to_page_filter(_, __, msg: Message) -> bool:
    """Filter for jump_to_page_handler."""
    try:
        return callback_matcher(
            clb=msg.reply_to_message.reply_markup.inline_keyboard[0][0].callback_data,
            data=JumpToPage
        )
    except (AttributeError, IndexError):
        return False


def callback_matcher(clb: CallbackQuery | str, data: type[CallbackData]) -> bool:
    """
    Check if the callback query matches the callback data.

    Args:
        clb: The callback query.
        data: The callback data.
    """
    return (clb.data if isinstance(clb, CallbackQuery) else clb).startswith(data.__clbname__)


@lru_cache
def get_browse_type_data(browse_type: BrowseTypeEnum) -> tuple[Callable[[], list[Any]], s, s, int]:
    """
    Helper function to get the data for a browse type.

    Args:
        browse_type: The browse type.

    Returns:
        ``Callable`` to get results, ``String`` for the browse type, ``String`` for the choose message, ``int`` for the number of columns.
    """
    if browse_type == BrowseTypeEnum.SUBJECT:
        return api.get_subjects, s.SUBJECTS, s.CHOOSE_SUBJECT, 2
    elif browse_type == BrowseTypeEnum.LETTER:
        return api.get_letters, s.LETTERS, s.CHOOSE_LETTER, 3
    elif browse_type == BrowseTypeEnum.DATERANGE:
        return api.get_date_ranges, s.DATE_RANGES, s.CHOOSE_DATE_RANGE, 2
    elif browse_type == BrowseTypeEnum.SHAS:
        return api.get_masechtot, s.SHAS, s.CHOOSE_MASECHET, 3
    raise ValueError(f"Invalid browse type: {browse_type}")
