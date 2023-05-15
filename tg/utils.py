from pyrogram import Client
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from tg import helpers
from tg.strings import String as s, get_string as gs
from data import api
from db import repository


def start(_: Client, mb: Message | CallbackQuery):
    """Start message"""
    if isinstance(mb, CallbackQuery) and mb.data.endswith("stats"):
        repository.press_candle(mb.from_user.id)
    candle_pressed_count = repository.get_candle_pressed_count()
    kwargs = dict(
        text=gs(mb, s.WELCOME),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(gs(mb, s.SEARCH), switch_inline_query_current_chat=""),
                    InlineKeyboardButton(gs(mb, s.BROWSE), callback_data="browse_menu"),
                ],
                [
                    InlineKeyboardButton(text=gs(mb, s.LIGHT_A_CANDLE).format(candle_pressed_count),
                                         callback_data="start_stats"),
                    InlineKeyboardButton("📤", switch_inline_query=""),
                ],
                [InlineKeyboardButton(text=gs(mb, s.GITHUB), url="https://github.com/david-lev/hebrewbooksbot")],
                [InlineKeyboardButton(text=gs(mb, s.HEBREWBOOKS_SITE), url="https://hebrewbooks.org")],
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
        if mb.data.endswith("stats"):
            users_count = repository.get_tg_users_count()
            stats = repository.get_stats()
            mb.answer(
                text="".join(gs(mb, s.STATS)).format(
                    users_count=users_count,
                    candle_pressed_count=candle_pressed_count,
                    books_read=stats.books_read, pages_read=stats.pages_read,
                    searches=stats.searches),
                show_alert=True,
                cache_time=300
            )


def show_book(_: Client, clb: CallbackQuery):
    """
    Show a book.

    clb.data: "show:book_id" + back_button_data
    """
    book_id, *clb_data = clb.data.split(':')[1:]
    book = api.get_book(int(book_id))
    clb.edit_message_text(
        text=helpers.get_book_text(book),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=gs(mqc=clb, string=s.BOOKS_READ),
                        callback_data=f"read:{book.id}:1:{book.pages}:show:{book.id}:{':'.join(clb_data)}"
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
                        text="🔙",
                        callback_data=":".join(clb_data)
                    )
                ] if clb_data != ["no_back"] else []
            ],
        )
    )
    repository.increase_books_read_count()


def read_book(_: Client, clb: CallbackQuery):
    """
    Read a book.

    clb.data: "read:book_id:page:total" + back_button_data
    """
    book_id, page, total, *clb_data = clb.data.split(':')[1:]
    book = api.get_book(book_id)
    next_previous_buttons = []
    if int(page) < int(total):
        next_previous_buttons.append(InlineKeyboardButton(
            text=gs(mqc=clb, string=s.NEXT),
            callback_data=f"read:{book_id}:{int(page) + 1}:{total}:{':'.join(clb_data)}"
        ))
    if int(page) > 1:
        next_previous_buttons.append(InlineKeyboardButton(
            text=gs(mqc=clb, string=s.PREVIOUS),
            callback_data=f"read:{book_id}:{int(page) - 1}:{total}:{':'.join(clb_data)}"
        ))
    clb.answer(
        text=gs(mqc=clb, string=s.WAIT_FOR_PREVIEW),
        show_alert=False
    )
    try:
        clb.edit_message_text(
            text="".join((
                "{}קריאה מהירה • עמוד {} מתוך {}\n\n".format(helpers.RTL, page, total),
                helpers.get_book_text(book, page=page),
            )),
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(text=f"📄 {page}/{total} 📄", callback_data=f"jump:{book_id}:{page}:{total}")],
                    [InlineKeyboardButton(text=gs(mqc=clb, string=s.READ_ON_SITE), url=book.get_page_url(page))],
                    next_previous_buttons,
                    [InlineKeyboardButton("🔙", callback_data=":".join(clb_data))],
                ]
            ),
        )
        repository.increase_pages_read_count()
    except MessageNotModified:
        clb.answer(
            text=gs(mqc=clb, string=s.SLOW_DOWN)
        )


def jump_to_page(_: Client, msg: Message):
    """
    Jump to a page.

    msg.text: number
    """
    book_id, page, total = msg.reply_to_message.reply_markup.inline_keyboard[0][0].callback_data.split(":")[1:]
    jump_to = int(msg.text)
    if jump_to > int(total):
        msg.reply_text(text=gs(mqc=msg, string=s.PAGE_NOT_EXIST).format(total))
        return

    book = api.get_book(book_id)
    new_next_previous_buttons = []
    next_or_previous = msg.reply_to_message.reply_markup.inline_keyboard[2:-1][0][0].callback_data.split(':')
    if jump_to < int(total):
        new_next_previous_buttons.append(InlineKeyboardButton(
            text=gs(mqc=msg, string=s.NEXT),
            callback_data=f"{':'.join(next_or_previous[:2])}:{jump_to + 1}:{':'.join(next_or_previous[3:])}"
        ))
    if jump_to > 1:
        new_next_previous_buttons.append(InlineKeyboardButton(
            text=gs(mqc=msg, string=s.PREVIOUS),
            callback_data=f"{':'.join(next_or_previous[:2])}:{jump_to - 1}:{':'.join(next_or_previous[3:])}"
        ))
    kwargs = dict(
        text="".join((
            "{}קריאה מהירה • עמוד {} מתוך {}\n\n".format(helpers.RTL, jump_to, total),
            helpers.get_book_text(book, page=jump_to),
        )),
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text=f"📄 {jump_to}/{total} 📄",
                                      callback_data=f"jump:{book_id}:{jump_to}:{total}")],
                [InlineKeyboardButton(text=gs(mqc=msg, string=s.READ_ON_SITE), url=book.get_page_url(jump_to))],
                new_next_previous_buttons,
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
