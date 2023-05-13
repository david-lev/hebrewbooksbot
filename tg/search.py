from pyrogram import Client
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, \
    InlineKeyboardButton, Message, CallbackQuery

from data import api
from tg import utils


def empty_search(_: Client, query: InlineQuery):
    query.answer(
        results=[
            InlineQueryResultArticle(
                id="1",
                title="התחילו לחפש",
                description="הקלד מילות חיפוש",
                input_message_content=InputTextMessageContent(
                    message_text="הקלד מילות חיפוש"
                )
            )
        ]
    )


def search_books_inline(_: Client, query: InlineQuery):
    if query.offset is not None and query.offset == '0':
        return
    title, author = query.query.split(':', 1) if ':' in query.query else (query.query, '')
    results, total = api.search(
        title=title.strip(),
        author=author.strip(),
        offset=int(query.offset or 1),
        limit=5
    )
    next_offset = utils.get_offset(int(query.offset or 1), total, increase=5)

    articles = [
        InlineQueryResultArticle(
            id=str(book.id),
            title=book.title,
            description=f"{book.author}{f' • {book.year}' if book.year else ''}{f' • {book.city}' if book.city else ''}",
            input_message_content=InputTextMessageContent(
                message_text=utils.get_book_text(book)
            ),
            reply_markup=InlineKeyboardMarkup(
                [utils.get_book_buttons(book)]
            ),
            thumb_url=book.cover_url
        ) for book in (api.get_book(b.id) for b in results)

    ]
    query.answer(
        switch_pm_text="{}{} תוצאות עבור {}".format(utils.RTL, total, f"{title}:{author}" if author else title),
        switch_pm_parameter="search",
        results=articles,
        next_offset=str(next_offset)
    )


def search_books_message(_: Client, msg: Message):
    title, author = msg.text.split(':', 1) if ':' in msg.text else (msg.text, '')
    results, total = api.search(
        title=title.strip(),
        author=author.strip(),
        offset=1,
        limit=5
    )
    if total == 0:
        msg.reply_text(
            text="לא נמצאו תוצאות עבור: {}".format(msg.text),
            quote=True
        )
        return
    next_offset = utils.get_offset(1, total, increase=5)
    next_previous_buttons = []
    if next_offset:
        next_previous_buttons.append(
            InlineKeyboardButton(
                text="הבא",
                callback_data=f"search:{next_offset}:{total}"
            )
        )
    msg.reply(
        text="{}{} תוצאות עבור: {}".format(utils.RTL, total, f"{title}:{author}" if author else title),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(book.title, callback_data=f"search:book:{book.id}:{1}:{total}")
                ] for book in results
            ] + [next_previous_buttons]
        ),
        quote=True
    )


def search_books_callback(_: Client, clb: CallbackQuery):
    offset, total = clb.data.split(':')[1:]
    search = clb.message.text.split(':', 1)[-1]
    title, author = search.split(':', 1) if ':' in search else (search, '')
    results, total = api.search(
        title=title.strip(),
        author=author.strip(),
        offset=int(offset),
        limit=5
    )
    next_offset = utils.get_offset(int(offset), int(total), increase=5)
    next_previous_buttons = []
    if next_offset:
        next_previous_buttons.append(
            InlineKeyboardButton(
                text="הבא",
                callback_data=f"search:{next_offset}:{total}"
            )
        )
    if int(offset) > 5:
        next_previous_buttons.append(
            InlineKeyboardButton(
                text="הקודם",
                callback_data=f"search:{int(offset) - 5}:{total}"
            )
        )
    clb.message.edit_reply_markup(
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(book.title, callback_data=f"search:book:{book.id}:{offset}:{total}")
                ] for book in results
            ] + [next_previous_buttons]
        )
    )


def search_book(_: Client, clb: CallbackQuery):
    book_id, offset, total = clb.data.split(':')[2:]
    book = api.get_book(book_id)
    clb.message.edit_text(
        text=utils.get_book_text(book),
        reply_markup=InlineKeyboardMarkup(
            [
                utils.get_book_buttons(book) +
                [InlineKeyboardButton("חזרה", callback_data=f"search:{offset}:{total}")]
            ]
        )
    )
