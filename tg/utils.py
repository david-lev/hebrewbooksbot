from pyrogram import Client, emoji
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from tg import helpers
from data import api
from db import repository


def start(_: Client, msg_or_callback: Message | CallbackQuery):
    """Start message"""
    kwargs = dict(
        text="".join((
            "**ברוכים הבאים להיברו-בוקס בטלגרם!**\n",
            "בוט זה מאפשר לכם לחפש ספרים באתר hebrewbooks.org ולקרוא אותם בטלגרם.\n",
            "לחצו על הכפתור המתאים לכם כדי להתחיל.\n\n",
        )),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🔎", switch_inline_query_current_chat=""),
                    InlineKeyboardButton("📚", callback_data="browse_menu"),
                    InlineKeyboardButton("📤", switch_inline_query=""),
                ],
                [InlineKeyboardButton("🌍 אתר היברובוקס 🌍", url="https://hebrewbooks.org")],
                [InlineKeyboardButton("⭐️ גיטהאב ⭐️", url="https://github.com/david-lev/hebrewbooksbot")]
            ]
        )
    )
    if isinstance(msg_or_callback, Message):
        msg_or_callback.reply_text(**kwargs)
        repository.add_tg_user(msg_or_callback.from_user.id)
    else:
        msg_or_callback.edit_message_text(**kwargs)


def show_book(_: Client, clb: CallbackQuery):
    """
    Show a book.

    clb.data: "show:book_id" + back_button_data
    """
    book_id, *clb_data = clb.data.split(':')[1:]
    book = api.get_book(int(book_id))
    print(f"read:{book.id}:1:{book.pages}:show:{book.id}:{':'.join(clb_data)}")
    clb.edit_message_text(
        text=helpers.get_book_text(book),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text=emoji.DOWN_ARROW, url=book.pdf_url),
                    InlineKeyboardButton(
                        text=emoji.OPEN_BOOK,
                        callback_data=f"read:{book.id}:1:{book.pages}:show:{book.id}:{':'.join(clb_data)}"
                    ),
                ],
                [InlineKeyboardButton("חזור", callback_data=":".join(clb_data))] if clb_data != ["no_back"] else []
            ]
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
            text="הבא ⏪",
            callback_data=f"read:{book_id}:{int(page) + 1}:{total}:{':'.join(clb_data)}"
        ))
    next_previous_buttons.append(
        InlineKeyboardButton(
            text=f"{page}/{total}",
            url=book.get_page_url(page)
        )
    )
    if int(page) > 1:
        next_previous_buttons.append(InlineKeyboardButton(
            text="⏩ הקודם",
            callback_data=f"read:{book_id}:{int(page) - 1}:{total}:{':'.join(clb_data)}"
        ))
    clb.answer(
        text='יש להמתין מספר שניות לטעינת התצוגה המקדימה',
        show_alert=False
    )
    clb.edit_message_text(
        text="".join((
            "{}קריאה מהירה • עמוד {} מתוך {}\n\n".format(helpers.RTL, page, total),
            helpers.get_book_text(book, page=page),
        )),
        reply_markup=InlineKeyboardMarkup(
            [
                next_previous_buttons,
                [InlineKeyboardButton("חזור", callback_data=":".join(clb_data))],
            ]
        ),
    )
    repository.increase_pages_read_count()


def jump_to_page(_: Client, msg: Message):
    """
    Jump to a page.

    msg.text: number
    """
    action, book_id, page, total, *clb_data = \
        msg.reply_to_message.reply_markup.inline_keyboard[0][0].callback_data.split(':')
    if int(msg.text) > int(total):
        msg.reply_text(text="העמוד לא קיים! (כמות עמודים: {})".format(total))
        return

    msg.reply_to_message.edit_text(

    )
