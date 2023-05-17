from pyrogram.types import Message, CallbackQuery
from data.models import Book
from tg.callbacks import CallbackData, JumpToPage

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
