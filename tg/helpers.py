from functools import lru_cache
from typing import Callable, Any
from pyrogram import filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineQuery
from sqlalchemy.orm import exc
from data import api, config
from data.models import Book, Masechet, Tursa
from data.enums import BrowseType as BrowseTypeEnum
from data.callbacks import CallbackData, JumpToPage, ReadMode, ReadBook, BookType
from data.strings import String as s, STRINGS, String, RTL, LTR
from db import repository

DEFAULT_LANGUAGE = "en"
CACHE_CHANNEL_ID = config.get_settings().tg_cache_channel_id


def get_lang_code(mqc: Message | CallbackQuery | InlineQuery) -> str:
    """Get the user's language code."""
    try:
        lang = mqc.from_user.language_code or DEFAULT_LANGUAGE
    except AttributeError:
        lang = DEFAULT_LANGUAGE
    return lang


def get_string(mqc: Message | CallbackQuery | InlineQuery, string: String) -> str:
    """Get a string in the user's language."""
    lang = get_lang_code(mqc)
    return STRINGS[string].get(lang, STRINGS[string][DEFAULT_LANGUAGE])


class Menu:
    START = 'start'
    BROADCAST = 'broadcast'
    BROWSE = 'browse_menu'
    STATS = 'stats'
    CONTACT_URL = 'https://t.me/davidlev'
    GITHUB_URL = 'https://github.com/david-lev/hebrewbooksbot'
    HEBREWBOOKS_SITE_URL = 'https://hebrewbooks.org'


MESSAGE_SEARCH_FILTER = (
        filters.text & ~filters.via_bot & ~filters.reply & ~filters.command([Menu.START, Menu.BROADCAST]) &
        ~filters.create(lambda _, __, msg: msg.text.isdigit())
        & ~filters.create(lambda _, __, ms: len(ms.text) <= 2)
)


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
        f"{RTL}👤 {book.author}\n" if book.author else "",
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
            text=get_string(cm, string) if new_read_mode is read_clb.read_mode else emoji,
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
            text=get_string(mqc=cm, string=s.NEXT),
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
            text=get_string(mqc=cm, string=s.PREVIOUS),
            callback_data=ReadBook(
                id=read_clb.id,
                page=page - 1,
                total=total,
                read_mode=read_clb.read_mode,
                book_type=read_clb.book_type
            ).join_to_callback(*others)
        ))
    return buttons if get_lang_code(cm) == "he" else buttons[::-1]


def get_file_id(
        send_method: Any,
        media_attr: str,
        url: str
) -> str:
    """
    Get the file id from the url.

    Args:
        send_method: The method to send the file (bound method of pyrogram.Client).
        media_attr: The attribute of the media to get the file id from.
        url: The url of the file.
    """
    max_attempts = 3
    while max_attempts:
        try:
            max_attempts -= 1
            return repository.get_tg_file(url).file_id
        except exc.NoResultFound:
            file = getattr(send_method(**{media_attr: url, 'chat_id': CACHE_CHANNEL_ID}), media_attr)
            repository.create_tg_file(url=url, file_id=file.file_id, file_uid=file.file_unique_id)
            continue
    raise ValueError(f"Could not get file id for {url}")
