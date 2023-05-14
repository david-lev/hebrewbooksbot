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
        utils.start, filters.create(lambda _, __, query: query.data == "start")
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
        browse.browse_types, filters=filters.create(
            lambda _, __, query: query.data.startswith("browse_type")
        )
    )
)

app.add_handler(
    CallbackQueryHandler(
        browse.browse_books_navigator, filters=filters.create(
            lambda _, __, query: query.data.startswith("browse_nav")
        )
    )
)

app.add_handler(
    MessageHandler(
        search.search_books_message, filters=(
                filters.text & ~filters.via_bot
        )
    )
)

app.add_handler(
    CallbackQueryHandler(
        search.search_books_navigator, filters=filters.create(
            lambda _, __, query: query.data.startswith("search_nav")
        )
    )
)

app.add_handler(
    CallbackQueryHandler(
        utils.show_book, filters=filters.create(lambda _, __, query: query.data.startswith("show_book"))
    )
)

app.add_handler(
    CallbackQueryHandler(
        utils.read_book, filters=filters.create(lambda _, __, query: query.data.startswith("read_book"))
    )
)


app.run()
