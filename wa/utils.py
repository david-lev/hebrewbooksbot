import dataclasses
from pywa import WhatsApp
from pywa.types import Message, CallbackSelection, InlineButton, CallbackButton
from data import api
from db import repository
from db.repository import StatsType
from data.callbacks import ShareBook, ReadBook, ReadMode, BookType, ShowBook
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


def show_book(_: WhatsApp, msg_or_cb: Message | CallbackSelection):
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
                callback_data=ReadBook(
                    id=str(book.id),
                    page=1,
                    total=book.pages,
                    read_mode=ReadMode.IMAGE,
                    book_type=BookType.BOOK
                ).to_callback()
            )
        ]
    )
    repository.increase_stats(StatsType.BOOKS_READ)


def read_book(_: WhatsApp, clb: CallbackButton):
    book, masechet, page = None, None, None
    read_clb = ReadBook.from_callback(clb.data)
    if read_clb.book_type == BookType.BOOK:
        book = api.get_book(int(read_clb.id))
        url = book.get_page_img(page=read_clb.page, width=750, height=1334) if read_clb.read_mode == ReadMode.IMAGE \
            else book.get_page_pdf(page=read_clb.page)
    elif read_clb.book_type == BookType.MASECHET:
        masechet = api.get_masechet(int(read_clb.id))
        page = masechet.pages[read_clb.page - 1]
        url = page.get_page_img(width=750, height=1334) if read_clb.read_mode == ReadMode.IMAGE else page.pdf_url
    else:
        raise NotImplementedError
    buttons = [
        InlineButton(
            title=gs(s.DOCUMENT if read_clb.read_mode == ReadMode.IMAGE else s.IMAGE),
            callback_data=dataclasses.replace(
                read_clb,
                read_mode=ReadMode.PDF if read_clb.read_mode == ReadMode.IMAGE else ReadMode.IMAGE
            ).to_callback()
        ),
    ]
    if read_clb.page < read_clb.total:
        buttons.append(InlineButton(
            title=gs(s.NEXT),
            callback_data=dataclasses.replace(read_clb, page=read_clb.page + 1).to_callback()
        ))
    if 1 < read_clb.page < read_clb.total:
        buttons.append(InlineButton(
            title=gs(s.PREVIOUS),
            callback_data=dataclasses.replace(read_clb, page=read_clb.page - 1).to_callback()
        ))
    caption = helpers.get_book_details(book) \
        if read_clb.book_type == BookType.BOOK else helpers.get_masechet_details(masechet)
    caption += f"\n{gs(s.PAGE_X_OF_Y, x=read_clb.page, y=read_clb.total)}"
    if read_clb.read_mode == ReadMode.IMAGE:
        clb.reply_image(image=url, buttons=buttons, caption=caption)
    elif read_clb.read_mode == ReadMode.PDF:
        file_name = f"{book.title} • {book.author} ({read_clb.page}).pdf" \
            if read_clb.book_type == BookType.BOOK else f"{masechet.name} ({page.name}).pdf"
        clb.reply_document(document=url, file_name=file_name, caption=caption, buttons=buttons)
    else:
        raise NotImplementedError

    repository.increase_stats(StatsType.PAGES_READ)


def on_share(_: WhatsApp, clb: CallbackButton):
    book_id = ShareBook.from_callback(clb.data).id
    book = api.get_book(book_id)
    clb.reply_text(
        text="".join((
            helpers.get_book_details(book),
            f"🔗 {helpers.get_self_share(ShowBook(book_id).to_callback())}",
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
