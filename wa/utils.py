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
    read = ReadBook.from_callback(clb.data)
    is_book = read.book_type == BookType.BOOK
    is_image = read.read_mode == ReadMode.IMAGE
    if is_book:
        book = api.get_book(int(read.id))
        url = book.get_page_img(page=read.page, width=750, height=1334) if is_image \
            else book.get_page_pdf(page=read.page)
    else:
        masechet = api.get_masechet(int(read.id))
        page = masechet.pages[read.page - 1]
        url = page.get_page_img(width=750, height=1334) if is_image else page.pdf_url
    func = clb.reply_image if is_image else clb.reply_document
    buttons = [
        InlineButton(
            title=gs(s.DOCUMENT if is_image else s.IMAGE),
            callback_data=dataclasses.replace(
                read,
                read_mode=ReadMode.PDF if is_image else ReadMode.IMAGE
            ).to_callback()
        ),
    ]
    if read.page < read.total:
        buttons.append(InlineButton(
            title=gs(s.NEXT),
            callback_data=dataclasses.replace(read, page=read.page + 1).to_callback()
        ))
    if read.page > 1:
        buttons.append(InlineButton(
            title=gs(s.PREVIOUS),
            callback_data=dataclasses.replace(read, page=read.page - 1).to_callback()
        ))
    caption = helpers.get_book_details(book) \
        if is_book else helpers.get_masechet_details(masechet)
    caption += f"\n{gs(s.PAGE_X_OF_Y, x=read.page, y=read.total)}"
    if is_image:
        kwargs = dict(image=url, caption=caption, buttons=buttons)
    else:
        file_name = f"{book.title} • {book.author} ({read.page}).pdf" \
            if is_book else f"{masechet.name} ({page.name}).pdf"
        kwargs = dict(document=url, file_name=file_name, caption=caption, buttons=buttons)
    func(**kwargs)
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
