from pyrogram import Client
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, \
    InlineKeyboardButton, Message, CallbackQuery
from data import api
from data.models import Book
from db import repository
from tg import helpers
from tg.callbacks import SearchNavigation, ShowBook
from tg.strings import String as s, get_string as gs


def empty_search(_: Client, query: InlineQuery):
    """Show a message when the user searches for nothing"""
    query.answer(
        results=[
            InlineQueryResultArticle(
                id="1",
                title=gs(mqc=query, string=s.START_SEARCH_INLINE),
                description=gs(mqc=query, string=s.SEARCH_INLINE_TIP),
                input_message_content=InputTextMessageContent(
                    message_text="/start"
                )
            )
        ]
    )


def _get_book_article(book: Book, query: InlineQuery) -> InlineQueryResultArticle:
    """
    Internal function to get an article for a book
    """
    return InlineQueryResultArticle(
        id=str(book.id),
        title=book.title,
        description=f"{book.author}{f' • {book.year}' if book.year else ''}{f' • {book.city}' if book.city else ''}",
        input_message_content=InputTextMessageContent(
            message_text=helpers.get_book_text(book)
        ),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=gs(mqc=query, string=s.PREVIOUS),
                        callback_data=f"read:{book.id}:1:{book.pages}:show:{book.id}:no_back"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=gs(mqc=query, string=s.SHARE),
                        switch_inline_query=str(book.id)
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=gs(mqc=query, string=s.DOWNLOAD),
                        url=book.pdf_url
                    ),
                ]
            ]
        ),
        thumb_url=book.get_page_img(page=1, width=100, height=100),
    )


def search_books_inline(_: Client, query: InlineQuery):
    """
    Search books inline

    query.query format: "{title}" / "{title}:{author}"
    """
    if query.offset is not None and query.offset == '0':
        return  # No more results

    if query.query.isdigit():  # The user searched for a book id
        book = api.get_book(int(query.query))
        if book is None:
            query.answer(
                results=[],
                switch_pm_text=gs(mqc=query, string=s.BOOK_NOT_FOUND),
                switch_pm_parameter="search"
            )
            return
        query.answer(
            results=[_get_book_article(book, query)],
            switch_pm_text=gs(mqc=query, string=s.PRESS_TO_SHARE).format(book.title),
            switch_pm_parameter="search"
        )
        repository.increase_books_read_count()
        return

    title, author = helpers.get_title_author(query.query)
    results, total = api.search(
        title=title.strip(),
        author=author.strip(),
        offset=int(query.offset or 1),
        limit=5
    )
    query.answer(
        switch_pm_text="{}{} תוצאות עבור {}".format(helpers.RTL, total, f"{title}:{author}" if author else title),
        switch_pm_parameter="search",
        results=[_get_book_article(book, query=query) for book in (api.get_book(b.id) for b in results)],
        next_offset=str(helpers.get_offset(int(query.offset or 1), total, increase=5))
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
            text=gs(mqc=msg, string=s.NO_RESULTS_FOR_S).format(msg.text),
            quote=True
        )
        return
    next_offset = helpers.get_offset(1, total, increase=5)
    next_previous_buttons = []
    if next_offset:
        next_previous_buttons.append(
            InlineKeyboardButton(
                text=gs(mqc=msg, string=s.NEXT),
                callback_data=SearchNavigation(offset=next_offset, total=total).to_callback()
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
                [InlineKeyboardButton(gs(mqc=msg, string=s.SEARCH_INLINE), switch_inline_query_current_chat=msg.text)]
            ]
        ),
        quote=True
    )
    repository.increase_search_count()


def search_books_navigator(_: Client, clb: CallbackQuery):
    """
    Navigate through search results
    """
    search_nav = SearchNavigation.from_callback(clb)
    try:
        search = clb.message.reply_to_message.text
        if not search:
            raise AttributeError
    except AttributeError:
        clb.answer(gs(mqc=clb, string=s.ORIGINAL_SEARCH_DELETED), show_alert=True)
        return

    title, author = helpers.get_title_author(search)
    results, total = api.search(
        title=title.strip(),
        author=author.strip(),
        offset=search_nav.offset,
        limit=5
    )
    next_offset = helpers.get_offset(search_nav.offset, int(total), increase=5)
    next_previous_buttons = []
    if next_offset:
        next_previous_buttons.append(
            InlineKeyboardButton(
                text=gs(mqc=clb, string=s.NEXT),
                callback_data=SearchNavigation(offset=next_offset, total=total).to_callback()
            )
        )
    if search_nav.offset > 5:
        next_previous_buttons.append(
            InlineKeyboardButton(
                text=gs(mqc=clb, string=s.PREVIOUS),
                callback_data=SearchNavigation(offset=search_nav.offset - 5, total=total).to_callback()
            )
        )
    clb.message.edit_text(
        text="{}{} תוצאות עבור: {}".format(helpers.RTL, total, search),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=book.title,
                        callback_data=f"show:{book.id}:search_nav:{search_nav.offset}:{total}"
                    )
                ] for book in results
            ] + [
                next_previous_buttons,
                [InlineKeyboardButton(gs(mqc=clb, string=s.SEARCH_INLINE), switch_inline_query_current_chat=search)]
            ]
        )
    )
