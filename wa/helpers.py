from data.config import get_settings
from data.models import Book
from data.strings import STRINGS, String

conf = get_settings()

DEFAULT_LANGUAGE = "he"


def get_self_share(text: str) -> str:
    """
    Get the link to share a text on WhatsApp.

    Args:
        text: The text to share.
    """
    return f"https://wa.me/{conf.wa_phone_number}?text={text}"


def get_string(string: String, **kwargs) -> str:
    """Get a string from the strings file."""
    return STRINGS[string].get(DEFAULT_LANGUAGE).format(**kwargs)


def slice_long_string(string: str, max_length: int, suffix: str = "...") -> str:
    """Slice a long string."""
    return string[:max_length - len(suffix)] + suffix if len(string) > max_length else string


def get_book_details(book: Book):
    return "".join((
        f"📚 {book.title}\n",
        f"👤 {book.author}\n",
        f"📅 {book.year}\n" if book.year else "",
        f"🏙 {book.city}\n" if book.city else "",
        f"📖 {book.pages}\n",
    ))
