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
    SEARCH = 'search'
    ABOUT = 'about'
    STATS = 'stats'
    CONTACT_URL = 'https://t.me/davidlev'
    GITHUB_URL = 'https://github.com/david-lev/hebrewbooksbot'
    HEBREWBOOKS_SITE_URL = 'https://hebrewbooks.org'


def show_book(_: WhatsApp, msg_or_cb: Message | CallbackSelection):
    try:
        show = ShowBook.from_callback(msg_or_cb.text if isinstance(msg_or_cb, Message) else msg_or_cb.data)
    except ValueError:
        msg_or_cb.react("❌")
        msg_or_cb.reply_text(
            text=gs(s.NUMBERS_ONLY),
            quote=True
        )
        return
    if (book := api.get_book(show.id)) is None:
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
        footer=gs(s.IN_MEMORY_FOOTER),
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


def read_book(_: WhatsApp, msg_or_clb: Message | CallbackButton):
    book, masechet, page = None, None, None
    if isinstance(msg_or_clb, Message):
        try:
            read = ReadBook.from_cmd(msg_or_clb.text)
        except ValueError:
            msg_or_clb.react("❌")
            msg_or_clb.reply_text(
                text=gs(s.NUMBERS_ONLY),
                quote=True
            )
            return
    else:
        read = ReadBook.from_callback(msg_or_clb.data)
    is_book = read.book_type == BookType.BOOK
    is_image = read.read_mode == ReadMode.IMAGE
    if is_book:
        try:
            book = api.get_book(int(read.id))
        except ValueError:
            msg_or_clb.react("❌")
            msg_or_clb.reply_text(text=gs(s.BOOK_NOT_FOUND), quote=True)
            return
        if book is None:
            msg_or_clb.react("❌")
            msg_or_clb.reply_text(
                text=gs(s.BOOK_NOT_FOUND),
                quote=True
            )
            return
        try:
            url = book.get_page_img(page=read.page, width=750, height=1334) if is_image \
                else book.get_page_pdf(page=read.page)
        except ValueError:
            msg_or_clb.react("❌")
            msg_or_clb.reply_text(
                text=gs(s.PAGE_NOT_EXIST_CHOOSE_BETWEEN_X_Y, x=1, y=book.pages),
                quote=True
            )
            return
    else:
        try:
            masechet = api.get_masechet(int(read.id))
        except ValueError:
            msg_or_clb.react("❌")
            msg_or_clb.reply_text(text=gs(s.MASECHET_NOT_FOUND), quote=True)
            return
        try:
            page = masechet.pages[read.page - 1]
        except IndexError:
            msg_or_clb.react("❌")
            msg_or_clb.reply_text(
                text=gs(s.PAGE_NOT_EXIST_CHOOSE_BETWEEN_X_Y, x=masechet.pages[0].name, y=masechet.pages[-1].name),
                quote=True
            )
            return
        url = page.get_page_img(width=750, height=1334) if is_image else page.pdf_url

    func = msg_or_clb.reply_image if is_image else msg_or_clb.reply_document
    total = book.pages if is_book else len(masechet.pages)
    buttons = [
        InlineButton(
            title=gs(s.DOCUMENT if is_image else s.IMAGE),
            callback_data=dataclasses.replace(
                read,
                read_mode=ReadMode.PDF if is_image else ReadMode.IMAGE
            ).to_callback()
        ),
    ]
    if read.page < total:
        buttons.append(InlineButton(
            title=gs(s.NEXT),
            callback_data=dataclasses.replace(read, page=read.page + 1).to_callback()
        ))
    if read.page > 1:
        buttons.append(InlineButton(
            title=gs(s.PREVIOUS),
            callback_data=dataclasses.replace(read, page=read.page - 1).to_callback()
        ))
    if is_image:
        kwargs = dict(image=url, buttons=buttons)
    else:
        file_name = f"{book.title} • {book.author} ({read.page}).pdf" \
            if is_book else f"{masechet.name} ({page.name}).pdf"
        kwargs = dict(document=url, file_name=file_name, buttons=buttons)
    if isinstance(msg_or_clb, Message):
        msg_or_clb.react("⬆️")
    caption = helpers.get_page_details(book, gs(s.PAGE_X_OF_Y, x=read.page, y=total)) \
        if is_book else helpers.get_masechet_details(masechet)
    func(**kwargs, footer=gs(s.IN_MEMORY_FOOTER), caption=caption)
    repository.increase_stats(StatsType.PAGES_READ)


def on_share_btn(_: WhatsApp, clb: CallbackButton):
    book_id = ShareBook.from_callback(clb.data).id
    book = api.get_book(book_id)
    clb.reply_text(
        text="".join((
            helpers.get_book_details(book),
            f"🔗 {helpers.get_self_share(ShowBook(book_id).to_callback())}",
        )),
        quote=True,
    )


def on_search_btn(_: WhatsApp, clb: CallbackButton):
    clb.reply_text(
        text=f"{gs(s.SEARCH_INSTRUCTIONS)}\n{gs(s.SEARCH_TIP)}",
        keyboard=[InlineButton(title=gs(s.BACK), callback_data=Menu.START)],
        footer=gs(s.PYWA_CREDIT),
    )


def on_stats_btn(_: WhatsApp, clb: CallbackButton):
    clb.reply_text(
        text=helpers.get_stats(clb.from_user),
        footer=gs(s.PYWA_CREDIT),
        keyboard=[InlineButton(title=gs(s.BACK), callback_data=Menu.START)],
    )


def on_about_btn(_: WhatsApp, clb: CallbackButton):
    clb.reply_text(
        text=gs(s.WA_ABOUT_MSG),
        footer=gs(s.PYWA_CREDIT),
        keyboard=[InlineButton(title=gs(s.BACK), callback_data=Menu.START)],
    )


def on_start(_: WhatsApp, msg_or_clb: Message | CallbackButton):
    msg_or_clb.reply_text(
        header=gs(s.WA_WELCOME_HEADER),
        text=gs(s.WA_WELCOME_BODY),
        keyboard=[
            InlineButton(
                title=gs(s.SEARCH),
                callback_data=Menu.SEARCH
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
        footer=gs(s.IN_MEMORY_FOOTER),
    )
