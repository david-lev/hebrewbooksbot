from pywa import WhatsApp
from pywa.types import Message, CallbackSelection, InlineButton, CallbackButton
from data import api
from data.callbacks import ShareBook, ReadBook
from data.strings import String as s
from wa import helpers
from wa.helpers import get_string as gs


class Menu:
    START = 'start'
    ABOUT = 'about'
    BROWSE = 'browse_menu'
    STATS = 'stats'
    CONTACT_URL = 'https://t.me/davidlev'
    GITHUB_URL = 'https://github.com/david-lev/hebrewbooksbot'
    HEBREWBOOKS_SITE_URL = 'https://hebrewbooks.org'


def on_book(_: WhatsApp, msg_or_cb: Message | CallbackSelection):
    try:
        book = api.get_book(
            int((msg_or_cb.data if isinstance(msg_or_cb, CallbackSelection) else msg_or_cb.text).split(":")[1])
        )
    except ValueError:
        msg_or_cb.react("❌")
        msg_or_cb.reply_text(
            text=gs(s.BOOK_NOT_FOUND),
            quote=True
        )
        return
    if book is None:
        msg_or_cb.react("❌")
        msg_or_cb.reply_text(
            text=gs(s.BOOK_NOT_FOUND),
            quote=True
        )
        return
    msg_or_cb.react("⬆️")
    msg_or_cb.reply_document(
        document=book.pdf_url,
        file_name=f"{book.title} • {book.author}.pdf",
        caption=helpers.get_book_details(book),
        footer=gs(s.WA_WELCOME_FOOTER),
        quote=True,
        buttons=[
            InlineButton(
                title=gs(s.SHARE),
                callback_data=ShareBook(book.id).to_callback()
            ),
            InlineButton(
                title=gs(s.INSTANT_READ),
                callback_data=ReadBook(book.id).to_callback()
            )
        ]
    )


def on_share(_: WhatsApp, clb: CallbackButton):
    book_id = int(clb.data.split(":")[1])
    book = api.get_book(book_id)
    clb.reply_text(
        text="".join((
            helpers.get_book_details(book),
            f"🔗 {helpers.get_self_share(f'!book:{book_id}')}"
        )),
        quote=True,
    )


def on_start(_: WhatsApp, msg: Message):
    msg.reply_text(
        header=gs(s.WA_WELCOME_HEADER),
        text=gs(s.WA_WELCOME_BODY),
        keyboard=[
            InlineButton(
                title=gs(s.BROWSE),
                callback_data=Menu.BROWSE
            ),
            InlineButton(
                title=gs(s.STATS),
                callback_data=Menu.STATS
            ),
            InlineButton(
                title=gs(s.ABOUT),
                callback_data=Menu.ABOUT
            )
        ],
        footer=gs(s.WA_WELCOME_FOOTER),
    )
