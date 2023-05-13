from pyrogram import Client, emoji
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from data import api
from data.models import Book

RTL = '\u200f'
LTR = '\u200e'


def get_book_text(book: Book, page: int | None = None) -> str:
    """
    Get the text for a book.

    Args:
        book: The book.
        page: If provided, the page url will be added to the text, else the pdf url will be added.
    """
    return "".join((
        f"{RTL}[📚]({book.pdf_url if page is None else book.get_page_url(page, width=2138, height=3038)}) {book.title}\n",
        f"{RTL}👤 {book.author}\n",
        f"{RTL}📅 {book.year}\n" if book.year else "",
        f"{RTL}🏙 {book.city}\n" if book.city else "",
        f"{RTL}📖 {book.pages}\n",
    ))


def get_book_buttons(book: Book) -> list[InlineKeyboardButton]:
    """
    Get the buttons for a book.

    Args:
        book: The book.
    """
    return [
        InlineKeyboardButton(emoji.DOWN_ARROW, url=book.pdf_url),
        InlineKeyboardButton(emoji.OPEN_BOOK, callback_data=f"read:{book.id}:1:{book.pages}")
    ]


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


def start(_: Client, msg_or_callback: Message | CallbackQuery):
    kwargs = {
        'text': (
            "ברוכים הבאים לבוט היברו בוקס!\n"
            "הבוט מאפשר לכם לחפש ספרים באתר hebrewbooks.org ולקרוא אותם בטלגרם.\n"
        ),
        'reply_markup': InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("חיפוש", switch_inline_query_current_chat="")],
                [InlineKeyboardButton("חיפוש בצ'אט אחר", switch_inline_query="")],
                [InlineKeyboardButton("עיון", callback_data="browse_menu")],
                [InlineKeyboardButton("לאתר", url="https://hebrewbooks.org")]
            ]
        )
    }
    if isinstance(msg_or_callback, Message):
        msg_or_callback.reply_text(**kwargs)
    else:
        msg_or_callback.edit_message_text(**kwargs)


def read(_: Client, clb: CallbackQuery):
    _, book_id, page, total = clb.data.split(':')
    book = api.get_book(book_id)
    next_previous_buttons = []
    if int(page) > 1:
        next_previous_buttons.append(InlineKeyboardButton(
            emoji.LEFT_ARROW,
            callback_data=f"read:{book_id}:{int(page) - 1}:{total}"
        ))
    if int(page) < int(total):
        next_previous_buttons.append(InlineKeyboardButton(
            emoji.RIGHT_ARROW,
            callback_data=f"read:{book_id}:{int(page) + 1}:{total}"
        ))

    clb.edit_message_text(
        text="".join((
            "{}קריאה מהירה • עמוד {} מתוך {}\n\n".format(RTL, page, total),
            get_book_text(book, page=page),
        )),
        reply_markup=InlineKeyboardMarkup(
            [
                next_previous_buttons,
                [InlineKeyboardButton("חזור", callback_data=f"book:{book_id}")]
            ]
        ),
    )
