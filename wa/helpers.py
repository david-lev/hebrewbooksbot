from data.config import get_settings
from data.models import Book, Masechet
from data.strings import STRINGS, String, RTL

conf = get_settings()

DEFAULT_LANGUAGE = "he"


class Commands:
    SHAS = ('shas', 'שס')
    SUBJECT = ('sub', 'נושא')
    DATERANGE = ('date', 'תאריך')
    LETTER = ('let', 'אות')
    TURSA = ('tur', 'טור')


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
        f"{RTL}📖 {book.pages}\n",
    ))


def get_masechet_details(masechet: Masechet):
    return "".join((
        f"📚 {masechet.name}\n",
        f"{RTL}📖 {masechet.pages[0].name}- {masechet.pages[-1].name}\n"
    ))
