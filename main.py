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
    InlineQueryHandler(search.search_books_inline, filters=filters.create(lambda _, __, query: len(query.query) > 2)),
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
        browse.browse, filters=filters.create(
            lambda _, __, query: query.data.startswith("browse") and len(query.data.split(":")) == 2
        )
    )
)

app.add_handler(
    CallbackQueryHandler(
        browse.browse_results, filters=filters.create(
            lambda _, __, query: query.data.startswith("browse") and len(query.data.split(":")) == 5
        )
    )
)

app.add_handler(
    MessageHandler(
        search.search_books_message, filters=(
                filters.text & ~filters.via_bot & filters.create(lambda _, __, msg: len(msg.text) > 2))
    )
)

app.add_handler(
    CallbackQueryHandler(
        search.search_books_callback, filters=filters.create(
            lambda _, __, query: query.data.startswith("search") and len(query.data.split(":")) == 3
        )
    )
)

app.add_handler(
    CallbackQueryHandler(
        utils.read, filters=filters.create(lambda _, __, query: query.data.startswith("read"))
    )
)

app.add_handler(
    CallbackQueryHandler(
        browse.browse_book, filters=filters.create(
            lambda _, __, query: query.data.startswith("browse:book")
        )
    )
)

app.add_handler(
    CallbackQueryHandler(
        search.search_book, filters=filters.create(
            lambda _, __, query: query.data.startswith("search:book")
        )
    )
)

app.run()
