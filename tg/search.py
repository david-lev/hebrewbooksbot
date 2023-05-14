from pyrogram import Client
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, \
    InlineKeyboardButton, Message, CallbackQuery
from data import api
from db import repository
from tg import helpers


def empty_search(_: Client, query: InlineQuery):
    """Show a message when the user searches for nothing"""
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
    """
    Search books inline

    query.query format: "{title}" / "{title}:{author}"
    """
    if query.offset is not None and query.offset == '0':
        return
    title, author = helpers.get_title_author(query.query)
    results, total = api.search(
        title=title.strip(),
        author=author.strip(),
        offset=int(query.offset or 1),
        limit=5
    )
    next_offset = helpers.get_offset(int(query.offset or 1), total, increase=5)

    articles = [
        InlineQueryResultArticle(
            id=str(book.id),
            title=book.title,
            description=f"{book.author}{f' • {book.year}' if book.year else ''}{f' • {book.city}' if book.city else ''}",
            input_message_content=InputTextMessageContent(
                message_text=helpers.get_book_text(book)
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="⬇️ הורדה ⬇️", url=book.pdf_url),
                        InlineKeyboardButton(
                            text="📖 קריאה מהירה 📖",
                            callback_data=f"read:{book.id}:1:{book.pages}:show:{book.id}:no_back"
                        ),
                    ],
                ]
            ),
            thumb_url=book.get_page_img(page=1, width=100, height=100),
        ) for book in (api.get_book(b.id) for b in results)

    ]
    query.answer(
        switch_pm_text="{}{} תוצאות עבור {}".format(helpers.RTL, total, f"{title}:{author}" if author else title),
        switch_pm_parameter="search",
        results=articles,
        next_offset=str(next_offset)
    )
    repository.increase_search_count()


def search_books_message(_: Client, msg: Message):
    """
    Search books from a message

    msg.text format: "{title}" / "{title}:{author}"
    """
    title, author = helpers.get_title_author(msg.text)
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
    next_offset = helpers.get_offset(1, total, increase=5)
    next_previous_buttons = []
    if next_offset:
        next_previous_buttons.append(
            InlineKeyboardButton(
                text="הבא ⏪",
                callback_data=f"search_nav:{next_offset}:{total}"
            )
        )
    msg.reply(
        text="{}{} תוצאות עבור: {}".format(helpers.RTL, total, f"{title}:{author}" if author else title),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=book.title,
                        callback_data=f"show:{book.id}:search_nav:{1}:{total}"
                    )
                ] for book in results
            ] + [
                next_previous_buttons,
                [InlineKeyboardButton("🔎 חיפוש באינליין", switch_inline_query_current_chat=msg.text)]
            ]
        ),
        quote=True
    )
    repository.increase_search_count()


def search_books_navigator(_: Client, clb: CallbackQuery):
    """
    Navigate through search results

    clb.data format: "search_nav:{offset}:{total}" + back_button_data
    """
    offset, total, *clb_data = clb.data.split(':')[1:]
    try:
        search = clb.message.reply_to_message.text
        if not search:
            raise AttributeError
    except AttributeError:
        clb.answer("החיפוש המקורי נמחק", show_alert=True)
        return

    title, author = helpers.get_title_author(search)
    results, total = api.search(
        title=title.strip(),
        author=author.strip(),
        offset=int(offset),
        limit=5
    )
    next_offset = helpers.get_offset(int(offset), int(total), increase=5)
    next_previous_buttons = []
    if next_offset:
        next_previous_buttons.append(
            InlineKeyboardButton(
                text="הבא ⏪",
                callback_data=f"search_nav:{next_offset}:{total}"
            )
        )
    if int(offset) > 5:
        next_previous_buttons.append(
            InlineKeyboardButton(
                text="⏩ הקודם",
                callback_data=f"search_nav:{int(offset) - 5}:{total}"
            )
        )
    clb.message.edit_text(
        text="{}{} תוצאות עבור: {}".format(helpers.RTL, total, search),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=book.title,
                        callback_data=f"show:{book.id}:search_nav:{offset}:{total}"
                    )
                ] for book in results
            ] + [
                next_previous_buttons,
                [InlineKeyboardButton("🔎 חיפוש באינליין", switch_inline_query_current_chat=search)]
            ]
        )
    )
