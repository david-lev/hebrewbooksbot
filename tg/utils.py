from pyrogram import Client
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from tg import helpers
from tg.helpers import Menu
from tg.callbacks import ShowBook, ReadBook, JumpToPage
from tg.strings import String as s, get_string as gs
from data import api
from db import repository


def start(_: Client, mb: Message | CallbackQuery):
    """Start message"""
    if isinstance(mb, CallbackQuery) and mb.data == Menu.STATS:
        repository.press_candle(mb.from_user.id)
    candle_pressed_count = repository.get_candle_pressed_count()
    kwargs = dict(
        text=gs(mb, s.WELCOME),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(gs(mb, s.SEARCH), switch_inline_query_current_chat=""),
                    InlineKeyboardButton(gs(mb, s.BROWSE), callback_data=Menu.BROWSE),
                ],
                [
                    InlineKeyboardButton(
                        text=gs(mb, s.LIGHT_A_CANDLE).format(count=candle_pressed_count),
                        callback_data=Menu.STATS
                    ),
                    InlineKeyboardButton("📤", switch_inline_query=""),
                ],
                [InlineKeyboardButton(text=gs(mb, s.GITHUB), url=Menu.GITHUB_URL)],
                [InlineKeyboardButton(text=gs(mb, s.HEBREWBOOKS_SITE), url=Menu.HEBREWBOOKS_SITE_URL)],
            ]
        )
    )
    if isinstance(mb, Message):
        mb.reply_text(**kwargs)
        repository.add_tg_user(mb.from_user.id, mb.from_user.language_code)
    else:
        try:
            mb.edit_message_text(**kwargs)
        except MessageNotModified:
            pass
        if mb.data == Menu.STATS:
            users_count = repository.get_tg_users_count()
            stats = repository.get_stats()
            mb.answer(
                text="".join(gs(mb, s.STATS)).format(
                    users_count=users_count,
                    candle_pressed_count=candle_pressed_count,
                    books_read=stats.books_read, pages_read=stats.pages_read,
                    searches=stats.searches
                ),
                show_alert=True,
                cache_time=300
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
                        callback_data=ReadBook(id=book.id, page=1, total=book.pages).join_to_callback(
                            ShowBook(id=book.id), *others
                        )
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
    repository.increase_books_read_count()


def read_book(_: Client, clb: CallbackQuery):
    """
    Read a book.
    """
    _read_book, *others = clb.data.split(',')
    read_clb = ReadBook.from_callback(_read_book)
    book = api.get_book(read_clb.id)
    next_previous_buttons = []
    if read_clb.page < read_clb.total:
        next_previous_buttons.append(InlineKeyboardButton(
            text=gs(mqc=clb, string=s.NEXT),
            callback_data=ReadBook(id=read_clb.id, page=read_clb.page + 1, total=read_clb.total).join_to_callback(*others)
        ))
    if read_clb.page > 1:
        next_previous_buttons.append(InlineKeyboardButton(
            text=gs(mqc=clb, string=s.PREVIOUS),
            callback_data=ReadBook(id=read_clb.id, page=read_clb.page - 1, total=read_clb.total).join_to_callback(*others)
        ))
    clb.answer(
        text=gs(mqc=clb, string=s.WAIT_FOR_PREVIEW),
        show_alert=False
    )
    try:
        clb.edit_message_text(
            text="".join((
                gs(mqc=clb, string=s.INSTANT_READ),
                "\n\n",
                helpers.get_book_text(book, page=read_clb.page),
            )),
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(
                        text=f"📄 {read_clb.page}/{read_clb.total} 📄",
                        callback_data=JumpToPage(read_clb.id, read_clb.page, read_clb.total).to_callback()
                    )],
                    [InlineKeyboardButton(text=gs(mqc=clb, string=s.READ_ON_SITE), url=book.get_page_url(read_clb.page))],
                    next_previous_buttons,  # TODO reverse in RTL
                    [InlineKeyboardButton(text=gs(mqc=clb, string=s.BACK), callback_data=",".join(others))],
                ]
            ),
        )
        repository.increase_pages_read_count()
    except MessageNotModified:
        clb.answer(
            text=gs(mqc=clb, string=s.SLOW_DOWN)
        )


def jump_to_page(client: Client, msg: Message):
    """
    Jump to a page.

    msg.text: number
    """
    jump_clb = JumpToPage.from_callback(msg.reply_to_message.reply_markup.inline_keyboard[0][0].callback_data)
    jump_to = int(msg.text)
    if jump_to > jump_clb.total or jump_to < 1:
        msg.reply_text(text=gs(mqc=msg, string=s.PAGE_NOT_EXIST).format(total=jump_clb.total))
        return

    book = api.get_book(jump_clb.id)
    new_next_previous_buttons = []
    _next_or_previous, *nop_others = msg.reply_to_message.reply_markup.inline_keyboard[2:-1][0][0].callback_data.split(',')
    nop_clb = ReadBook.from_callback(_next_or_previous)
    if jump_to < jump_clb.total:
        new_next_previous_buttons.append(InlineKeyboardButton(
            text=gs(mqc=msg, string=s.NEXT),
            callback_data=ReadBook(
                id=nop_clb.id,
                page=jump_to + 1,
                total=nop_clb.total
            ).join_to_callback(*nop_others)
        ))
    if jump_to > 1:
        new_next_previous_buttons.append(InlineKeyboardButton(
            text=gs(mqc=msg, string=s.PREVIOUS),
            callback_data=ReadBook(
                id=nop_clb.id,
                page=jump_to - 1,
                total=nop_clb.total
            ).join_to_callback(*nop_others)
        ))
    kwargs = dict(
        text="".join((
            gs(mqc=msg, string=s.INSTANT_READ),
            "\n\n",
            helpers.get_book_text(book, page=jump_to),
        )),
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(
                    text=f"📄 {jump_to}/{jump_clb.total} 📄",
                    callback_data=JumpToPage(id=jump_clb.id, page=jump_to, total=jump_clb.total).to_callback()
                )],
                [InlineKeyboardButton(text=gs(mqc=msg, string=s.READ_ON_SITE), url=book.get_page_url(jump_to))],
                new_next_previous_buttons,  # TODO reverse in RTL
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


def jump_tip(_: Client, clb: CallbackQuery):
    """
    Jump to a page tip.

    clb.data: "jump:*"
    """
    clb.answer(
        text=gs(mqc=clb, string=s.JUMP_TIP),
        show_alert=True
    )
