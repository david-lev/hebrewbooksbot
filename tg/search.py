from pyrogram import Client
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, \
    InlineKeyboardButton, Message, CallbackQuery
from data import api
from data.models import Book
from db import repository
from db.repository import StatsType
from tg import helpers
from tg.callbacks import SearchNavigation, ShowBook, ReadBook, ReadMode, BookType
from tg.strings import String as s, get_string as gs, get_lang_code as glc


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


def _get_book_article(book: Book, query: InlineQuery, read_at_page: int) -> InlineQueryResultArticle:
    """
    Internal function to get an article for a book

    Args:
        book: The book
        query: The inline query
        read_at_page: The page to show when the user clicks on the "Read" button
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
                        text=gs(mqc=query, string=s.INSTANT_READ),
                        callback_data=ReadBook(
                            id=book.id,
                            page=read_at_page,
                            total=book.pages,
                            read_mode=ReadMode.IMAGE,
                            book_type=BookType.BOOK
                        ).join_to_callback(ShowBook(id=book.id))
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
    print(query.query)
    if query.offset is not None and query.offset == '0':
        return  # No more results

    if all(part.isdigit() for part in query.query.split(':')):  # The user searched for a book id or a book id:page
        if ':' in query.query:
            book_id, page = map(int, query.query.split(':'))
            page = page or 1
        else:
            book_id, page = int(query.query), 1
        book = api.get_book(book_id)
        if book is None:
            query.answer(
                results=[],
                switch_pm_text=gs(mqc=query, string=s.BOOK_NOT_FOUND),
                switch_pm_parameter="search"
            )
            return
        if page > book.pages:
            query.answer(
                results=[],
                switch_pm_text=gs(mqc=query, string=s.PAGE_NOT_EXIST).format(start=1, total=book.pages),
                switch_pm_parameter="search"
            )
            return
        query.answer(
            results=[_get_book_article(book=book, query=query, read_at_page=page)],
            switch_pm_text=gs(mqc=query, string=s.PRESS_TO_SHARE).format(title=book.title),
            switch_pm_parameter="search"
        )
        repository.increase_stats(StatsType.BOOKS_READ)
        return

    title, author = helpers.get_title_author(query.query)
    results, total = api.search(
        title=title.strip(),
        author=author.strip(),
        offset=int(query.offset or 1),
        limit=5
    )
    query.answer(
        switch_pm_text=gs(query, s.X_RESULTS_FOR_S).format(
            x=total, s=f"{title}:{author}" if author else title
        ),
        switch_pm_parameter="search",
        results=[_get_book_article(book=book, query=query, read_at_page=1) for book in (api.get_book(b.id) for b in results)],
        next_offset=str(helpers.get_offset(int(query.offset or 1), total, increase=5))
    )
    repository.increase_stats(StatsType.INLINE_SEARCHES)


def search_books_message(_: Client, msg: Message):
    """
    Search books from a message

    msg.text format: "{title}" / "{title}:{author}"
    """
    title, author = helpers.get_title_author(msg.text)
    results, total = api.search(
        title=title,
        author=author,
        offset=1,
        limit=5
    )
    if total == 0:
        msg.reply_text(
            text=gs(mqc=msg, string=s.NO_RESULTS_FOR_S).format(query=msg.text),
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
        text=gs(msg, s.X_TO_Y_OF_TOTAL_FOR_S).format(
            x=1, y=(next_offset - 1) if next_offset else total, total=total, s=msg.text
        ),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=book.title,
                        callback_data=ShowBook(id=book.id).join_to_callback(SearchNavigation(offset=1, total=total))
                    )
                ] for book in results
            ] + [
                next_previous_buttons,
                [InlineKeyboardButton(gs(mqc=msg, string=s.SEARCH_INLINE), switch_inline_query_current_chat=msg.text)]
            ]
        ),
        quote=True
    )
    repository.increase_stats(StatsType.MSG_SEARCHES)


def search_books_navigator(_: Client, clb: CallbackQuery):
    """
    Navigate through search results
    """
    search_nav = SearchNavigation.from_callback(clb.data)
    try:
        search = clb.message.reply_to_message.text
        if not search:
            raise AttributeError
    except AttributeError:
        clb.answer(gs(mqc=clb, string=s.ORIGINAL_SEARCH_DELETED), show_alert=True)
        return

    title, author = helpers.get_title_author(search)
    results, total = api.search(
        title=title,
        author=author,
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
        text=gs(clb, s.X_TO_Y_OF_TOTAL_FOR_S).format(
            x=search_nav.offset, y=(next_offset - 1) if next_offset else total, total=total, s=search
        ),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=book.title,
                        callback_data=ShowBook(id=book.id).join_to_callback(search_nav)
                    )
                ] for book in results
            ] + [
                next_previous_buttons if glc(clb) == "he" else next_previous_buttons[::-1],
                [InlineKeyboardButton(gs(mqc=clb, string=s.SEARCH_INLINE), switch_inline_query_current_chat=search)]
            ]
        )
    )
