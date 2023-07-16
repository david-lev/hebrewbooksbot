from pywa.types.others import User
from data.config import get_settings
from data.models import Book, Masechet
from data.strings import STRINGS, RTL, String as s
from urllib import parse
from db import repository

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
    return f"https://wa.me/{conf.wa_phone_number}?text={parse.quote_plus(text)}"


def is_admin(wa_user: User) -> bool:
    """Check if a user is an admin."""
    return wa_user.wa_id in conf.wa_admins


def get_string(string: s, **kwargs) -> str:
    """Get a string from the strings file."""
    return STRINGS[string].get(DEFAULT_LANGUAGE).format(**kwargs)


gs = get_string  # internal alias


def slice_long_string(string: str, max_length: int, suffix: str = "...") -> str:
    """Slice a long string."""
    return string[:max_length - len(suffix)] + suffix if len(string) > max_length else string


def get_book_details(book: Book) -> str:
    return "".join((
        f"📚 {book.title}\n",
        f"👤 {book.author}\n" if book.author else "",
        f"📅 {book.year}\n" if book.year else "",
        f"🏙 {book.city}\n" if book.city else "",
        f"{RTL}📖 {book.pages}\n",
    ))


def get_page_details(book: Book, page_status: str) -> str:
    return "".join((
        f"📚 {book.title}\n",
        f"👤 {book.author}\n" if book.author else "",
        f"📅 {book.year}\n" if book.year else "",
        f"🏙 {book.city}\n" if book.city else "",
        f"📖 {page_status}\n",
    ))


def get_stats(wa_user: User):
    stats = repository.get_stats()
    if is_admin(wa_user):
        return gs(
            string=s.SHOW_STATS_ADMIN,
            tg_users_count=repository.get_tg_users_count(),
            wa_users_count=repository.get_wa_users_count(),
            books_read=stats.books_read,
            pages_read=stats.pages_read,
            inline_searches=stats.inline_searches,
            msg_searches=stats.msg_searches,
            jumps=stats.jumps,
        )
    else:
        return gs(
            string=s.SHOW_STATS,
            books_read=stats.books_read,
            pages_read=stats.pages_read,
            searches=stats.searches
        )


def get_masechet_details(masechet: Masechet):
    return "".join((
        f"📚 {masechet.name}\n",
        f"{RTL}📖 {masechet.pages[0].name}- {masechet.pages[-1].name}\n"
    ))
