from pyrogram import Client
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, \
    InlineKeyboardButton, Message

from data import api


def search_books(_: Client, query: InlineQuery):
    results, total = api.search(
        title=query.query,
        offset=int(query.offset or 0),
        limit=10
    )
    current_offset = int(query.offset or 0)
    offset = current_offset + 10 if total > current_offset + 10 else ""
    query.answer(
        results=[
            InlineQueryResultArticle(
                id=str(book.id),
                title=book.title,
                description=book.author,
                input_message_content=InputTextMessageContent(
                    book.pdf_url,
                ),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("Upload", callback_data=f"action_upload_{book.id}"),
                            InlineKeyboardButton("Download", url=book.pdf_url),
                            InlineKeyboardButton("Read", url=f"https://hebrewbooks.org/pdfpager.aspx?req={book.id}")
                        ]
                    ]
                ),
                thumb_url=book.cover_url
            ) for book in (api.get_book(b.id) for b in results)

        ],
        next_offset=str(offset)
    )


def search_books(_: Client, msg: Message):
    kb = [[InlineKeyboardButton(
        text=f"{book.title} | {book.author}",
        callback_data=f"book_{book.id}")]
        for book in (b.to_book() for b in api.search(msg.text)[0])
    ]

    kb.append([InlineKeyboardButton(text="Next", callback_data=f"action_next_10_{msg.text}")])

    msg.reply_text(
        text="Results",
        reply_markup=InlineKeyboardMarkup(kb)
    )
