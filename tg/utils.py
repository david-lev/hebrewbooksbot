from pyrogram import Client
from pyrogram.errors import MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from tg import helpers
from data import api
from db import repository


def start(_: Client, msg_or_callback: Message | CallbackQuery):
    """Start message"""
    if isinstance(msg_or_callback, CallbackQuery) and msg_or_callback.data.endswith("stats"):
        repository.press_candle(msg_or_callback.from_user.id)
    candle_pressed_count = repository.get_candle_pressed_count()
    kwargs = dict(
        text="".join((
            "**📚 ברוכים הבאים להיברו-בוקס בטלגרם! 📚**\n\n",
            "🔎 בוט זה מאפשר חיפוש ועיון ספרים באתר hebrewbooks.org\n",
            "**📜 הוראות שימוש:** לחצו על חיפוש או על דפדוף כדי להתחיל או פשוט שלחו מילת חיפוש.\n",
            "**💡 טיפ:** ניתן לחפש בפורמט `כותר:מחבר` כדי לקבל תוצאות מדוייקות יותר.\n\n",
            "__🕯 לעילוי נשמת סבי הרב אהרן יצחק בן שמואל זנוויל זצ״ל 🕯__\n\n",
        )),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🔎 חיפוש 🔎", switch_inline_query_current_chat=""),
                    InlineKeyboardButton("📚 דפדוף 📚", callback_data="browse_menu"),
                ],
                [
                    InlineKeyboardButton(f"🕯 {candle_pressed_count:,} 🕯", callback_data="start_stats"),
                    InlineKeyboardButton("📤", switch_inline_query=""),
                ],
                [InlineKeyboardButton("⭐️ גיטהאב ⭐️", url="https://github.com/david-lev/hebrewbooksbot")],
                [InlineKeyboardButton("🌍 אתר היברובוקס 🌍", url="https://hebrewbooks.org")],
            ]
        )
    )
    if isinstance(msg_or_callback, Message):
        msg_or_callback.reply_text(**kwargs)
        repository.add_tg_user(msg_or_callback.from_user.id, msg_or_callback.from_user.language_code)
    else:
        try:
            msg_or_callback.edit_message_text(**kwargs)
        except MessageNotModified:
            pass
        if msg_or_callback.data.endswith("stats"):
            users_count = repository.get_tg_users_count()
            stats = repository.get_stats()
            msg_or_callback.answer(
                text="".join((
                    "📊 סטטיסטיקות הבוט 📊\n\n",
                    f"👥 משתמשים רשומים: {users_count}\n", \
                    f"🕯 נרות הודלקו: {candle_pressed_count}\n"
                    f"📚 ספרים נקראו: {stats.books_read}\n",
                    f"📖 עמודים נקראו: {stats.pages_read}\n",
                    f"🔎 חיפושים בוצעו: {stats.searches}\n",
                )),
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
                        text="📖 קריאה מהירה 📖",
                        callback_data=f"read:{book.id}:1:{book.pages}:show:{book.id}:{':'.join(clb_data)}"
                    )
                ], [
                    InlineKeyboardButton(
                        text="♻️ שיתוף ♻️",
                        switch_inline_query=str(book.id)
                    )
                ],
                [
                    InlineKeyboardButton(text="⬇️ הורדה ⬇️", url=book.pdf_url)
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
            text="הבא ⏪",
            callback_data=f"read:{book_id}:{int(page) + 1}:{total}:{':'.join(clb_data)}"
        ))
    if int(page) > 1:
        next_previous_buttons.append(InlineKeyboardButton(
            text="⏩ הקודם",
            callback_data=f"read:{book_id}:{int(page) - 1}:{total}:{':'.join(clb_data)}"
        ))
    clb.answer(
        text='יש להמתין מספר שניות לטעינת התצוגה המקדימה',
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
                    [InlineKeyboardButton(text=f"🌍 קריאה באתר 🌍", url=book.get_page_url(page))],
                    next_previous_buttons,
                    [InlineKeyboardButton("🔙", callback_data=":".join(clb_data))],
                ]
            ),
        )
        repository.increase_pages_read_count()
    except MessageNotModified:
        clb.answer(
            text="אני לא מלאך.. לאט יותר"
        )


def jump_to_page(_: Client, msg: Message):
    """
    Jump to a page.

    msg.text: number
    """
    book_id, page, total = msg.reply_to_message.reply_markup.inline_keyboard[0][0].callback_data.split(":")[1:]
    jump_to = int(msg.text)
    if jump_to > int(total):
        msg.reply_text(text="העמוד לא קיים! (כמות עמודים: {})".format(total))
        return

    book = api.get_book(book_id)
    kwargs = dict(
        text="".join((
            "{}קריאה מהירה • עמוד {} מתוך {}\n\n".format(helpers.RTL, jump_to, total),
            helpers.get_book_text(book, page=jump_to),
        )),
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text=f"📄 {jump_to}/{total} 📄", callback_data=f"jump:{book_id}:{jump_to}:{total}")],
                [InlineKeyboardButton(text=f"🌍 קריאה באתר 🌍", url=book.get_page_url(page))],
                *msg.reply_to_message.reply_markup.inline_keyboard[2:]
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
        text="טיפ: במקום לדפדף, הגיבו על ההודעה הזו עם מספר העמוד שברצונכם לקרוא",
        show_alert=True
    )
