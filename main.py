from pyrogram import Client, filters
from pyrogram.handlers import InlineQueryHandler

from tg import search
from tg.search import search_books, empty_search

app = Client("my_session")

app.add_handler(
    InlineQueryHandler(search_books, filters=filters.create(lambda _, __, query: len(query.query) > 2)),
)
app.add_handler(
    InlineQueryHandler(empty_search, filters=filters.create(lambda _, __, query: len(query.query) <= 2))
)

app.run()
