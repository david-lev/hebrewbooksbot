from urllib import parse
from pywa import WhatsApp
from data.config import get_settings
from data.models import Book, Masechet
from data.strings import RTL, String as s, get_string as _gs  # noqa
from data.enums import Language
from db import repository
# from data.api import session as api_session
# from sqlalchemy.orm import exc
# from datetime import date, timedelta

conf = get_settings()


def get_string(wa_id: str, string: s, **kwargs) -> str:
    """Get a string from the strings file."""
    return _gs(string=string, lng=Language.from_code(repository.get_wa_user(wa_id=wa_id).lang), **kwargs)


gs = get_string  # internal alias


class Commands:
    SHAS = ('shas', 'שס')
    SUBJECT = ('sub', 'נושא')
    DATERANGE = ('date', 'תאריך')
    LETTER = ('let', 'אות')
    TURSA = ('tur', 'טור')


languages = {
    # Israel
    ("972",): Language.HE,
    # France
    ("33",): Language.FR,
    # United States & Canada, Switzerland, Ukraine, Russia, Germany, Italy, Netherlands, Belgium,
    # South Africa, Poland, Australia
    ("1", "41", "380", "7", "49", "39", "31", "32", "27", "48", "44", "61"): Language.EN,
    # Spain, Argentina, Panama
    ("54", "34", "507", "52", "55"): Language.ES,
}

SUPPORTED_COUNTRIES = tuple(code for codes in languages.keys() for code in codes)


def phone_number_to_lang(phone: str) -> Language:
    """Get the language from a phone number."""
    for prefixes, lang in languages.items():
        if phone.startswith(prefixes):
            return lang
    return Language.EN


def get_self_share(text: str) -> str:
    """
    Get the link to share a text on WhatsApp.

    Args:
        text: The text to share.
    """
    return f"wa.me/{conf.wa_phone_number}?text={parse.quote_plus(text)}"


def is_admin(wa_id: str) -> bool:
    """Check if a user is an admin."""
    return wa_id in conf.wa_admins


def slice_long_string(string: str, max_length: int, suffix: str = "...") -> str:
    """Slice a long string."""
    return string[:max_length - len(suffix)] + suffix if len(string) > max_length else string


def get_book_details(book: Book) -> str:
    return "\n".join(i for i in (
        f"{RTL}📚 {book.title}",
        f"{RTL}👤 {book.author}" if book.author else "",
        f"{RTL}📅 {book.year}" if book.year else "",
        f"{RTL}🏙 {book.city}" if book.city else "",
        f"{RTL}📖 {book.pages}",
    ) if i)


def get_page_details(wa_id: str, book: Book, page_status: str) -> str:
    return "\n".join(i for i in (
        f"*{gs(wa_id, s.INSTANT_READ)}*\n\n"
        f"{RTL}📚 {book.title}",
        f"{RTL}👤 {book.author}" if book.author else "",
        f"{RTL}📅 {book.year}" if book.year else "",
        f"{RTL}🏙 {book.city}" if book.city else "",
        f"{RTL}📖 {page_status.strip()}\n",
        f"_💡{gs(wa_id, s.JUMP_TIP)}_",
    ) if i)


def get_masechet_details(masechet: Masechet):
    return "".join((
        f"📚 {masechet.name}\n",
        f"{RTL}📖 {masechet.pages[0].name}- {masechet.pages[-1].name}\n"
    ))


def get_file_id(wa: WhatsApp, url: str, file_name: str, mime_type: str) -> str:
    """
    Wrapper to get a file id from a url.
    """
    return url
    # max_attempts = 3
    # while max_attempts:
    #     try:
    #         max_attempts -= 1
    #         exists = repository.get_wa_file(url=url)
    #         if exists.upload_date < (date.today() - timedelta(days=30)):
    #             repository.delete_wa_file(url=url)
    #             raise exc.NoResultFound
    #         return exists.file_id
    #     except exc.NoResultFound:
    #         file_id = wa.upload_media(media=api_session.get(url).content, mime_type=mime_type, filename=file_name)
    #         repository.create_wa_file(url=url, file_id=file_id)
    #         continue
    # raise ValueError(f"Could not get file id for {url}")
