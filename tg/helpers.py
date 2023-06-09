from functools import lru_cache
from typing import Callable, Any
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineQuery
from data import api, config
from data.models import Book, Masechet, Tursa
from data.enums import BrowseType as BrowseTypeEnum
from tg.callbacks import CallbackData, JumpToPage, ReadMode, ReadBook, BookType
from tg.strings import String as s, get_string as gs, get_lang_code as glc

RTL = '\u200f'
LTR = '\u200e'


class Menu:
    START = 'start'
    BROADCAST = 'broadcast'
    BROWSE = 'browse_menu'
    STATS = 'stats'
    CONTACT_URL = 'https://t.me/davidlev'
    GITHUB_URL = 'https://github.com/david-lev/hebrewbooksbot'
    HEBREWBOOKS_SITE_URL = 'https://hebrewbooks.org'


def is_admin(mqc: Message | CallbackQuery | InlineQuery) -> bool:
    """
    Check if the user is an admin.
    """
    return mqc.from_user.id in config.get_settings().tg_admins


def get_book_text(book: Book, page: int | None = None, read_mode: ReadMode | None = None) -> str:
    """
    Get the text for a book.

    Args:
        book: The book.
        page: The page number.
        read_mode: The read mode.
    """
    match read_mode:
        case ReadMode.PDF:
            url = book.get_page_pdf(page)
        case ReadMode.IMAGE:
            url = book.get_page_img(page, width=2138, height=3038)
        case None:
            url = book.pdf_url
        case _:
            raise ValueError(f"Invalid read mode: {read_mode}")
    return "".join((
        f"{RTL}[📚]({url}) {book.title}\n",
        f"{RTL}👤 {book.author}\n",
        f"{RTL}📅 {book.year}\n" if book.year else "",
        f"{RTL}🏙 {book.city}\n" if book.city else "",
        f"{RTL}📖 {book.pages}\n",
    ))


def get_masechet_page_text(masechet: Masechet, page: int, read_mode: ReadMode) -> str:
    """
    Get the text for a masechet.

    Args:
        masechet: The masechet.
        page: The page number.
        read_mode: The read mode.
    """
    page_obj = masechet.pages[page - 1]
    match read_mode:
        case ReadMode.PDF:
            url = page_obj.pdf_url
        case ReadMode.IMAGE:
            url = page_obj.get_page_img(width=2138, height=3038)
        case _:
            raise ValueError(f"Invalid read mode: {read_mode}")
    return "".join((
        f"{RTL}[📚]({url}) {masechet.name}\n",
        f"{RTL}📄 {page_obj.name}"
    ))


def get_tursa_text(tursa: Tursa, previous_tursa: Tursa) -> str:
    """
    Get the text for a tursa.

    Args:
        tursa: The tursa.
        previous_tursa: The previous tursa.
    """
    return f"{RTL}[📚]({tursa.pdf_url}) {tursa.name} • {previous_tursa.name}"


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
        return any(
            callback_matcher(
                clb=clb,
                data=JumpToPage
            ) for clb in msg.reply_to_message.reply_markup.inline_keyboard[1]
        )
    except (AttributeError, IndexError):
        return False


def callback_matcher(clb: CallbackQuery | InlineKeyboardButton | str, data: type[CallbackData]) -> bool:
    """
    Check if the callback query matches the callback data.

    Args:
        clb: The callback query.
        data: The callback data.
    """
    return (
        clb.data if isinstance(clb, CallbackQuery)
        else clb.callback_data if isinstance(clb, InlineKeyboardButton)
        else clb
    ).startswith(data.__clbname__)


@lru_cache
def get_browse_type_data(
        browse_type: BrowseTypeEnum
) -> tuple[Callable[[str | None], list[Any]] | Callable[[], list[Any]], s, int]:
    """
    Helper function to get the data for a browse type.

    Args:
        browse_type: The browse type.

    Returns:
        ``Callable`` to get results, ``String`` for the choose message, ``int`` for the number of columns.
    """
    if browse_type == BrowseTypeEnum.SUBJECT:
        return api.get_subjects, s.CHOOSE_SUBJECT, 2
    elif browse_type == BrowseTypeEnum.LETTER:
        return api.get_letters, s.CHOOSE_LETTER, 3
    elif browse_type == BrowseTypeEnum.DATERANGE:
        return api.get_date_ranges, s.CHOOSE_DATE_RANGE, 2
    elif browse_type == BrowseTypeEnum.SHAS:
        return api.get_masechtot, s.CHOOSE_MASECHET, 3
    elif browse_type == BrowseTypeEnum.TURSA:
        return api.get_tursa, s.TUR_AND_SA, 1
    raise ValueError(f"Invalid browse type: {browse_type}")


def read_mode_chooser(
        cm: CallbackQuery | Message,
        read_clb: ReadBook,
        page: int,
        others: list[str],
        read_modes: list[ReadMode] = (ReadMode.PDF, ReadMode.IMAGE),
) -> list[InlineKeyboardButton]:
    """
    Get the read mode chooser buttons.

    Args:
        cm: The callback query or message.
        read_clb: The read book callback data.
        page: The current page.
        others: The other callback data to join to the callback data.
        read_modes: The read modes to choose from. (default: (ReadMode.PDF, ReadMode.IMAGE))
    """
    modes = list(filter(
        lambda rm: rm[0] in read_modes, (
            (ReadMode.PDF, "📄", s.DOCUMENT),
            (ReadMode.IMAGE, "🖼", s.IMAGE),
            (ReadMode.TEXT, "📝", s.TEXT)
        )
    ))
    if not modes:
        return []
    return [
        InlineKeyboardButton(
            text=gs(cm, string) if new_read_mode is read_clb.read_mode else emoji,
            callback_data=ReadBook(
                id=read_clb.id,
                page=page,
                total=read_clb.total,
                read_mode=new_read_mode,
                book_type=read_clb.book_type
            ).join_to_callback(*others)
        ) for new_read_mode, emoji, string in modes
    ]


def next_previous_buttons(
        cm: CallbackQuery | Message,
        read_clb: ReadBook,
        page: int,
        total: int,
        others: list[str],
) -> list[InlineKeyboardButton]:
    """
    Get the next and previous buttons.

    Args:
        cm: The callback query or message.
        read_clb: The read book callback data.
        page: The current page.
        total: The total number of pages.
        others: The other callback data to join to the callback data.
    """
    buttons = []
    if not total:
        return buttons
    if page < total:
        buttons.append(InlineKeyboardButton(
            text=gs(mqc=cm, string=s.NEXT),
            callback_data=ReadBook(
                id=read_clb.id,
                page=page + 1,
                total=total,
                read_mode=read_clb.read_mode,
                book_type=read_clb.book_type
            ).join_to_callback(*others)
        ))

    if read_clb.book_type == BookType.BOOK:
        buttons.append(
            InlineKeyboardButton(
                text=f"< {page}/{total} >",
                callback_data=JumpToPage(
                    id=int(read_clb.id),
                    page=page,
                    total=total,
                    book_type=BookType.BOOK
                ).to_callback()
            )
        )
    elif read_clb.book_type == BookType.MASECHET:
        masechet = api.get_masechet(int(read_clb.id))
        current_page = masechet.pages[page - 1]
        last_page = masechet.pages[-1]
        buttons.append(
            InlineKeyboardButton(
                text=f"< {current_page.name} / {last_page.name} >",
                callback_data=JumpToPage(
                    id=int(read_clb.id),
                    page=page,
                    total=masechet.total,
                    book_type=BookType.MASECHET
                ).to_callback()
            )
        )

    if page > 1:
        buttons.append(InlineKeyboardButton(
            text=gs(mqc=cm, string=s.PREVIOUS),
            callback_data=ReadBook(
                id=read_clb.id,
                page=page - 1,
                total=total,
                read_mode=read_clb.read_mode,
                book_type=read_clb.book_type
            ).join_to_callback(*others)
        ))
    return buttons if glc(cm) == "he" else buttons[::-1]
