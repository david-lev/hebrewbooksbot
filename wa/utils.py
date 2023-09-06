import dataclasses
from pywa import WhatsApp
from pywa.types import Message, CallbackSelection, Button, CallbackButton, SectionList, Section, SectionRow
from data import api, config
from data.callbacks import ShareBook, ReadBook, ShowBook
from data.enums import BookType, ReadMode, Language
from data.strings import String as s  # noqa
from data.rate_limit import limiter, RateLimit
from db import repository
from db.repository import StatsType
from wa import helpers
from wa.helpers import get_string as gs, slice_long_string as sls

conf = config.get_settings()

MSG_TO_BOOK_CACHE: dict[str, ReadBook] = {}


class Menu:
    START = 'start'
    SEARCH = 'search'
    CHANGE_LANGUAGE = 'change_lang'
    ABOUT = 'about'
    STATS = 'stats'
    CONTACT_URL = 'https://t.me/davidlev'
    GITHUB_URL = 'https://github.com/david-lev/hebrewbooksbot'
    HEBREWBOOKS_SITE_URL = 'https://hebrewbooks.org'


def show_book(client: WhatsApp, msg_or_cb: Message | CallbackSelection):
    wa_id = msg_or_cb.from_user.wa_id
    try:
        show = ShowBook.from_callback(msg_or_cb.text if isinstance(msg_or_cb, Message) else msg_or_cb.data)
    except ValueError:
        msg_or_cb.react("❌")
        msg_or_cb.reply_text(
            text=gs(wa_id, s.NUMBERS_ONLY),
            quote=True
        )
        return
    if (seconds := limiter.get_seconds_to_wait(
            user_id=wa_id,
            rate_limit_type=RateLimit.PDF_FULL
    )) > 0:
        msg_or_cb.reply_text(
            text=gs(wa_id, (s.WAIT_X_MINUTES if seconds >= 60 else s.WAIT_X_SECONDS),
                    x=int(seconds // 60 if seconds >= 60 else seconds)),
            quote=True
        )
        return
    if (book := api.get_book(show.id)) is None:
        msg_or_cb.react("❌")
        msg_or_cb.reply_text(
            text=gs(wa_id, s.BOOK_NOT_FOUND),
            quote=True
        )
        return
    msg_or_cb.react("⬆️")
    read_btn = ReadBook(
        id=str(book.id),
        page=1,
        total=book.pages,
        read_mode=ReadMode.IMAGE,
        book_type=BookType.BOOK
    )
    message_id = msg_or_cb.reply_document(
        document=helpers.get_file_id(wa=client, url=book.pdf_url,
                                     file_name=(file_name := f"{book.title} • {book.author}.pdf"),
                                     mime_type='application/pdf'),
        filename=file_name,
        caption=helpers.get_book_details(book),
        footer=gs(wa_id, s.IN_MEMORY_FOOTER),
        quote=True,
        buttons=[
            Button(
                title=gs(wa_id, s.SHARE),
                callback_data=ShareBook(book.id).to_callback()
            ),
            Button(
                title=gs(wa_id, s.INSTANT_READ),
                callback_data=read_btn.to_callback()
            )
        ]
    )
    MSG_TO_BOOK_CACHE[message_id] = read_btn
    repository.increase_stats(StatsType.BOOKS_READ)


def read_book(client: WhatsApp, msg_or_clb: Message | CallbackButton, data: ReadBook | None = None) -> str | None:
    wa_id = msg_or_clb.from_user.wa_id
    book, masechet, page = None, None, None
    if data is not None:
        read = data
    elif isinstance(msg_or_clb, CallbackButton):
        read = ReadBook.from_callback(msg_or_clb.data)
    else:
        try:
            read = ReadBook.from_cmd(msg_or_clb.text)
        except ValueError:
            msg_or_clb.react("❌")
            msg_or_clb.reply_text(
                text=gs(wa_id, s.NUMBERS_ONLY),
                quote=True
            )
            return
    is_book = read.book_type == BookType.BOOK
    is_image = read.read_mode == ReadMode.IMAGE
    if (seconds := limiter.get_seconds_to_wait(
            user_id=wa_id,
            rate_limit_type=RateLimit.IMAGE_PAGE if is_image else RateLimit.PDF_PAGE
    )) > 0:
        msg_or_clb.reply_text(
            text=gs(wa_id, (s.WAIT_X_MINUTES if seconds >= 60 else s.WAIT_X_SECONDS),
                    x=int(seconds // 60 if seconds >= 60 else seconds)),
            quote=True
        )
        return
    if is_book:
        try:
            book = api.get_book(int(read.id))
            if book is None:
                raise ValueError
        except ValueError:
            msg_or_clb.react("❌")
            msg_or_clb.reply_text(text=gs(wa_id, s.BOOK_NOT_FOUND), quote=True)
            return
        try:
            url = book.get_page_img(page=read.page, width=750, height=1334) if is_image \
                else book.get_page_pdf(page=read.page)
        except ValueError:
            msg_or_clb.react("❌")
            msg_or_clb.reply_text(
                text=gs(wa_id, s.PAGE_NOT_EXIST_CHOOSE_BETWEEN_X_Y, x=1, y=book.pages),
                quote=True
            )
            return
    else:
        try:
            masechet = api.get_masechet(int(read.id))
        except ValueError:
            msg_or_clb.react("❌")
            msg_or_clb.reply_text(text=gs(wa_id, s.MASECHET_NOT_FOUND), quote=True)
            return
        try:
            page = masechet.pages[read.page - 1]
        except IndexError:
            msg_or_clb.react("❌")
            msg_or_clb.reply_text(
                text=gs(wa_id, s.PAGE_NOT_EXIST_CHOOSE_BETWEEN_X_Y,
                        x=masechet.pages[0].name, y=masechet.pages[-1].name),
                quote=True
            )
            return
        url = page.get_page_img(width=750, height=1334) if is_image else page.pdf_url

    func = msg_or_clb.reply_image if is_image else msg_or_clb.reply_document
    total = book.pages if is_book else len(masechet.pages)
    buttons = [
        Button(
            title=gs(wa_id, s.DOCUMENT if is_image else s.IMAGE),
            callback_data=dataclasses.replace(
                read,
                read_mode=ReadMode.PDF if is_image else ReadMode.IMAGE
            ).to_callback()
        ),
    ]
    if read.page < total:
        buttons.append(Button(
            title=gs(wa_id, s.NEXT),
            callback_data=dataclasses.replace(read, page=read.page + 1).to_callback()
        ))
    if read.page > 1:
        buttons.append(Button(
            title=gs(wa_id, s.PREVIOUS),
            callback_data=dataclasses.replace(read, page=read.page - 1).to_callback()
        ))
    if is_image:
        kwargs = dict(
            image=helpers.get_file_id(wa=client, url=url, file_name='image.png', mime_type='image/jpeg'),
            buttons=buttons
        )
    else:
        file_name = f"{book.title} • {book.author} ({read.page}).pdf" \
            if is_book else f"{masechet.name} ({page.name}).pdf"
        kwargs = dict(
            document=helpers.get_file_id(wa=client, url=url, file_name=file_name, mime_type='application/pdf'),
            filename=file_name, buttons=buttons)
    if isinstance(msg_or_clb, Message):
        msg_or_clb.react("⬆️")
    caption = helpers.get_page_details(wa_id, book, gs(wa_id, s.PAGE_X_OF_Y, x=read.page, y=total)) \
        if is_book else helpers.get_masechet_details(masechet)
    message_id = func(**kwargs, footer=gs(wa_id, s.IN_MEMORY_FOOTER), caption=caption)
    MSG_TO_BOOK_CACHE[message_id] = dataclasses.replace(read, total=total)
    repository.increase_stats(StatsType.PAGES_READ)
    return message_id


def jump_to_page(client: WhatsApp, msg: Message):
    wa_id = msg.from_user.wa_id
    try:
        jump = int(msg.text)
    except ValueError:
        msg.react("❌")
        msg.reply_text(text=gs(wa_id, s.NUMBERS_ONLY), quote=True)
        return
    if (read := MSG_TO_BOOK_CACHE.get(msg.reply_to_message.message_id)) is None:
        msg.react("❌")
        msg.reply_text(text=gs(wa_id, s.NO_BOOK_SELECTED), quote=True)
        return
    if jump > read.total or jump < 1:
        msg.react("❌")
        msg.reply_text(text=gs(wa_id, s.PAGE_NOT_EXIST_CHOOSE_BETWEEN_X_Y, x=1, y=read.total), quote=True)
        return
    msg.react("⬆️")
    message_id = read_book(client, msg, dataclasses.replace(read, page=jump))
    if message_id is not None:
        MSG_TO_BOOK_CACHE[message_id] = read
    repository.increase_stats(StatsType.JUMPS)


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
    wa_id = clb.from_user.wa_id
    clb.reply_text(
        text=f"{gs(wa_id, s.SEARCH_INSTRUCTIONS)}\n{gs(wa_id, s.SEARCH_TIP)}",
        keyboard=[Button(title=gs(wa_id, s.BACK), callback_data=Menu.START)],
        footer=gs(wa_id, s.PYWA_CREDIT),
    )


def on_stats_btn(_: WhatsApp, clb: CallbackButton):
    wa_id = clb.from_user.wa_id
    clb.reply_text(
        text=helpers.get_stats(wa_id),
        footer=gs(wa_id, s.PYWA_CREDIT),
        keyboard=[Button(title=gs(wa_id, s.BACK), callback_data=Menu.START)],
    )


def on_about_btn(_: WhatsApp, clb: CallbackButton):
    wa_id = clb.from_user.wa_id
    clb.reply_image(
        image='https://user-images.githubusercontent.com/42866208/253792713-07c75d45-4613-4ff8-a077-9d9b2f61f144.png',
        body=gs(wa_id, s.WA_ABOUT_MSG, contact_phone_number=conf.contact_phone),
        footer=gs(wa_id, s.PYWA_CREDIT),
        buttons=[Button(title=gs(wa_id, s.BACK), callback_data=Menu.START)],
    )


def on_start(_: WhatsApp, msg_or_clb: Message | CallbackButton | CallbackSelection):
    wa_id = msg_or_clb.from_user.wa_id
    msg_or_clb.reply_text(
        header=gs(wa_id, s.WA_WELCOME_HEADER),
        text=gs(wa_id, s.WA_WELCOME_BODY),
        keyboard=[
            Button(
                title=sls(gs(wa_id, s.SEARCH), 20),
                callback_data=Menu.SEARCH
            ),
            Button(
                title=sls(gs(wa_id, s.CHANGE_LANGUAGE), 20),
                callback_data=Menu.CHANGE_LANGUAGE,
            ),
            Button(
                title=sls(gs(wa_id, s.ABOUT), 20),
                callback_data=Menu.ABOUT
            )
        ],
        footer=sls(gs(wa_id, s.IN_MEMORY_FOOTER), 60)
    )


def on_change_language(_: WhatsApp, clb: CallbackButton):
    wa_id = clb.from_user.wa_id
    clb.reply_text(
        text=gs(wa_id, s.CHOOSE_LANGUAGE),
        keyboard=SectionList(
            button_title=sls(gs(wa_id, s.CHOOSE_LANGUAGE), 20),
            sections=(
                Section(
                    title=sls(gs(wa_id, s.CHOOSE_LANGUAGE), 24),
                    rows=tuple(
                        SectionRow(
                            title=f"{lang.flag} {lang.name}",
                            callback_data=f"lang:{lang.code}"
                        ) for lang in Language
                    )
                ),
            )
        )
    )


def on_language_selected(client: WhatsApp, clb: CallbackSelection):
    wa_id = clb.from_user.wa_id
    clb.react("✅")
    repository.update_wa_user(wa_id=wa_id, lang=Language.from_code(clb.data.split(':')[1]).code)
    clb.reply_text(text=gs(wa_id, s.LANGUAGE_CHANGED), quote=True)
    on_start(client, clb)
