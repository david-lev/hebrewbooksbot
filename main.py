from pyrogram import Client, filters
from pyrogram.handlers import InlineQueryHandler, MessageHandler, CallbackQueryHandler

from tg import search
from tg import browse
from tg import utils

app = Client("my_session")
app.add_handler(
    MessageHandler(
        utils.start, filters.command("start")
    )
)

app.add_handler(
    CallbackQueryHandler(
        utils.start, filters.create(lambda _, __, query: query.data == "start_menu")
    )
)

app.add_handler(
    InlineQueryHandler(search.search_books, filters=filters.create(lambda _, __, query: len(query.query) > 2)),
)
app.add_handler(
    InlineQueryHandler(search.empty_search, filters=filters.create(lambda _, __, query: len(query.query) <= 2))
)

app.add_handler(
    CallbackQueryHandler(
        browse.browse_menu, filters=filters.create(lambda _, __, query: query.data == "browse_menu")
    )
)

app.add_handler(
    CallbackQueryHandler(
        browse.browse, filters=filters.create(lambda _, __, query: query.data.startswith("browse_") and query.data != "browse_menu")
    )
)

app.run()
