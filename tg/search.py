from pyrogram import Client, emoji
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, \
    InlineKeyboardButton

from data import api
from tg.utils import get_offset

RTL = '\u200f'


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


def search_books(_: Client, query: InlineQuery):
    results, total = api.search(
        title=query.query,
        author='',
        offset=int(query.offset or 1),
        limit=5
    )
    articles = [
        InlineQueryResultArticle(
            id=str(book.id),
            title=book.title,
            description=f"{book.author} • {book.year} • {book.city}",
            input_message_content=InputTextMessageContent(
                message_text=(
                    f"{RTL}📚 {book.title}\n"
                    f"{RTL}👤 {book.author}\n"
                    f"{RTL}📅 {book.year}\n"
                    f"{RTL}🏙 {book.city}\n"
                    f"{RTL}📖 {book.pages}\n"
                )
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(emoji.UP_ARROW, callback_data=f"action_upload_{book.id}"),
                        InlineKeyboardButton(emoji.DOWN_ARROW, url=book.pdf_url),
                        InlineKeyboardButton(emoji.OPEN_BOOK, url=f"https://hebrewbooks.org/pdfpager.aspx?req={book.id}")
                    ]
                ]
            ),
            thumb_url=book.cover_url
        ) for book in (api.get_book(b.id) for b in results)

    ]
    query.answer(
        switch_pm_text="מספר תוצאות: " + str(total),
        switch_pm_parameter="search",
        results=articles,
        next_offset=str(get_offset(int(query.offset or 1), total, increase=5))
    )
