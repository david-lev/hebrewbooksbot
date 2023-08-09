from datetime import date
from functools import lru_cache
from urllib import parse
from pywa import WhatsApp
from pywa.types.others import User
from data.config import get_settings
from data.models import Book, Masechet
from data.strings import STRINGS, RTL, String as s
from db import repository
from data.api import session

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
    return f"wa.me/{conf.wa_phone_number}?text={parse.quote_plus(text)}"


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
        f"{RTL}📅 {book.year}\n" if book.year else "",
        f"🏙 {book.city}\n" if book.city else "",
        f"{RTL}📖 {book.pages}\n",
    ))


def get_page_details(book: Book, page_status: str) -> str:
    return "".join((
        f"*{gs(s.INSTANT_READ)}*\n\n"
        f"📚 {book.title}\n",
        f"👤 {book.author}\n" if book.author else "",
        f"{RTL}📅 {book.year}\n" if book.year else "",
        f"🏙 {book.city}\n" if book.city else "",
        f"📖 {page_status}\n",
        f"\n_💡{gs(s.JUMP_TIP)}_\n",
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


def url_to_media_id(wa: WhatsApp, url: str, file_name: str, mime_type: str) -> str:
    """Get the media ID from a URL."""
    today = date.today()
    return _url_to_media_id(
        wa=wa, url=url, year_month=f"{today.year}-{today.month}", file_name=file_name, mime_type=mime_type
    )


@lru_cache
def _url_to_media_id(wa: WhatsApp, url: str, file_name: str, year_month: str, mime_type: str) -> str:
    """Get the media ID from a URL. year_month is used for caching purposes."""
    return wa.upload_media(media=session.get(url).content, mime_type=mime_type, file_name=file_name)

