from pyrogram import Client
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from db.repository import StatsType
from tg import helpers
from tg.helpers import Menu
from tg.callbacks import ShowBook, ReadBook, JumpToPage, ReadMode, BookType
from strings import String as s, get_string as gs
from data import api
from db import repository


def start(_: Client, mc: Message | CallbackQuery):
    """Start message"""
    if isinstance(mc, Message):
        repository.add_tg_user(tg_id=mc.from_user.id, lang=mc.from_user.language_code)
    kwargs = dict(
        text=gs(mc, s.WELCOME),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(gs(mc, s.SEARCH), switch_inline_query_current_chat=""),
                    InlineKeyboardButton(gs(mc, s.BROWSE), callback_data=Menu.BROWSE),
                ],
                [
                    InlineKeyboardButton("📤", switch_inline_query=""),
                    InlineKeyboardButton(text=gs(mc, s.STATS), callback_data=Menu.STATS),
                    InlineKeyboardButton("📮", url=Menu.CONTACT_URL),
                ],
                [InlineKeyboardButton(text=gs(mc, s.GITHUB), url=Menu.GITHUB_URL)],
                [InlineKeyboardButton(text=gs(mc, s.HEBREWBOOKS_SITE), url=Menu.HEBREWBOOKS_SITE_URL)],
            ]
        )
    )
    if isinstance(mc, Message):
        mc.reply_text(**kwargs)
    else:
        try:
            mc.edit_message_text(**kwargs)
        except MessageNotModified:
            pass


def show_stats(_: Client, clb: CallbackQuery):
    """
    Show stats.
    """
    stats = repository.get_stats()
    if helpers.is_admin(clb):
        users_count = repository.get_tg_users_count()
        clb.answer(
            text="".join(gs(clb, s.SHOW_STATS_ADMIN)).format(
                users_count=users_count,
                books_read=stats.books_read,
                pages_read=stats.pages_read,
                inline_searches=stats.inline_searches,
                msg_searches=stats.msg_searches,
                jumps=stats.jumps,
            ),
            show_alert=True
        )
    else:
        clb.answer(
            text="".join(gs(clb, s.SHOW_STATS)).format(
                books_read=stats.books_read,
                pages_read=stats.pages_read,
                searches=stats.searches
            ),
            show_alert=True,
            cache_time=100
        )


def show_book(_: Client, clb: CallbackQuery):
    """
    Show a book.
    """
    _book_id, *others = clb.data.split(',')

    book = api.get_book(ShowBook.from_callback(_book_id).id)
    clb.edit_message_text(
        text=helpers.get_book_text(book),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=gs(mqc=clb, string=s.INSTANT_READ),
                        callback_data=ReadBook(
                            id=book.id,
                            page=1,
                            total=book.pages,
                            read_mode=ReadMode.IMAGE,
                            book_type=BookType.BOOK
                        ).join_to_callback(ShowBook(id=book.id), *others)
                    )
                ], [
                    InlineKeyboardButton(
                        text=gs(mqc=clb, string=s.SHARE),
                        switch_inline_query=str(book.id)
                    )
                ],
                [
                    InlineKeyboardButton(text=gs(mqc=clb, string=s.DOWNLOAD), url=book.pdf_url)
                ],
                [
                    InlineKeyboardButton(
                        text=gs(mqc=clb, string=s.BACK),
                        callback_data=",".join(others)
                    )
                ] if others else others
            ],
        )
    )
    repository.increase_stats(StatsType.BOOKS_READ)


def read_book(_: Client, clb: CallbackQuery):
    """
    Read a book.
    """
    _read_book, *others = clb.data.split(',')
    read_clb = ReadBook.from_callback(_read_book)
    is_book = read_clb.book_type == BookType.BOOK
    if is_book:
        book = api.get_book(read_clb.id)
        total = book.pages
    else:
        masechet = api.get_masechet(read_clb.id)
        total = masechet.total
    clb.answer(
        text=gs(mqc=clb, string=s.WAIT_FOR_PREVIEW),
        show_alert=False
    )
    try:
        clb.edit_message_text(
            text="".join((
                gs(mqc=clb, string=s.INSTANT_READ),
                "\n\n",
                helpers.get_book_text(book=book, page=read_clb.page, read_mode=read_clb.read_mode) if is_book
                else helpers.get_masechet_page_text(masechet=masechet, page=read_clb.page, read_mode=read_clb.read_mode)
            )),
            reply_markup=InlineKeyboardMarkup(
                [
                    helpers.read_mode_chooser(cm=clb, read_clb=read_clb, page=read_clb.page, others=others),
                    helpers.next_previous_buttons(
                        cm=clb,
                        read_clb=read_clb,
                        total=total,
                        page=read_clb.page,
                        others=others,
                        is_book=is_book
                    ),
                    [InlineKeyboardButton(
                        text=gs(mqc=clb, string=s.READ_ON_SITE),
                        url=book.get_page_url(read_clb.page) if is_book else masechet.pages[read_clb.page - 1].get_page_url()
                    )],
                    [InlineKeyboardButton(text=gs(mqc=clb, string=s.BACK), callback_data=",".join(others))],
                ]
            ),
        )
        repository.increase_stats(StatsType.PAGES_READ)
    except MessageNotModified:
        clb.answer(
            text=gs(mqc=clb, string=s.SLOW_DOWN)
        )


def jump_to_page(_: Client, msg: Message):
    """
    Jump to a page.

    msg.text: number
    """
    jump_button = next(filter(
        lambda b: helpers.callback_matcher(b.callback_data, JumpToPage),
        msg.reply_to_message.reply_markup.inline_keyboard[1]
    ))
    jump_clb = JumpToPage.from_callback(jump_button.callback_data)
    is_book = jump_clb.book_type == BookType.BOOK
    if not is_book:
        masechet = api.get_masechet(jump_clb.id)
        try:
            jump_to = masechet.pages.index(next(filter(lambda p: p.name == msg.text, masechet.pages))) + 1
        except (StopIteration, ValueError):
            msg.reply_text(text=gs(mqc=msg, string=s.PAGE_NOT_EXIST).format(
                start=masechet.pages[0].name,
                total=masechet.pages[-1].name
            ))
            return
    else:
        try:
            jump_to = int(msg.text)
            if jump_to > jump_clb.total or jump_to < 1:
                msg.reply_text(text=gs(mqc=msg, string=s.PAGE_NOT_EXIST).format(start=1, total=jump_clb.total))
        except ValueError:
            msg.reply_text(text=gs(mqc=msg, string=s.JUMP_NUMBERS_ONLY))
            return
        book = api.get_book(jump_clb.id)
    _next_or_previous = next(filter(
        lambda b: helpers.callback_matcher(
            b.callback_data, ReadBook
        ), msg.reply_to_message.reply_markup.inline_keyboard[1:-1][0])
    )
    next_or_previous, *nop_others = _next_or_previous.callback_data.split(',')
    nop_clb = ReadBook.from_callback(next_or_previous)
    kwargs = dict(
        text="".join((
            gs(mqc=msg, string=s.INSTANT_READ),
            "\n\n",
            helpers.get_book_text(book=book, page=jump_to, read_mode=nop_clb.read_mode)
            if is_book else helpers.get_masechet_page_text(masechet=masechet, page=jump_to, read_mode=nop_clb.read_mode)
        )),
        reply_markup=InlineKeyboardMarkup(
            [
                helpers.read_mode_chooser(cm=msg, read_clb=nop_clb, page=jump_to, others=nop_others),
                helpers.next_previous_buttons(
                    cm=msg,
                    read_clb=nop_clb,
                    total=jump_clb.total,
                    page=jump_to,
                    others=nop_others,
                    is_book=is_book
                ),
                [InlineKeyboardButton(
                    text=gs(mqc=msg, string=s.READ_ON_SITE),
                    url=book.get_page_url(jump_clb.page) if is_book else masechet.pages[jump_clb.page - 1].get_page_url()
                )],
                [msg.reply_to_message.reply_markup.inline_keyboard[-1][-1]]
            ]
        )
    )
    if msg.reply_to_message.via_bot:
        msg.reply(**kwargs)  # Can't edit messages sent by the user
    else:
        msg.reply_to_message.edit(
            **kwargs
        )
    repository.increase_stats(StatsType.PAGES_READ)
    repository.increase_stats(StatsType.JUMPS)


def jump_tip(_: Client, clb: CallbackQuery):
    """
    Jump to a page tip.
    """
    clb.answer(
        text=gs(mqc=clb, string=s.JUMP_TIP),
        show_alert=True
    )
