from pyrogram import Client, filters
from pyrogram.handlers import InlineQueryHandler, MessageHandler, CallbackQueryHandler, EditedMessageHandler
from data import config
from tg import search, helpers
from tg import browse
from tg import utils
from tg.helpers import jump_to_page_filter
from tg.callbacks import BrowseNavigation, BrowseType, ShowBook, SearchNavigation, ReadBook, JumpToPage

cfg = config.get_settings()

app = Client(
    name="hebrewbooksbot",
    workdir="../",
    api_id=cfg.tg_api_id,
    api_hash=cfg.tg_api_hash,
    bot_token=cfg.tg_bot_token
)

app.add_handler(
    MessageHandler(
        utils.start, filters=filters.command("start")
    )
)

app.add_handler(
    CallbackQueryHandler(
        utils.start, filters=filters.create(lambda _, __, query: query.data.startswith("start"))
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
            lambda _, __, query: helpers.callback_matcher(query, BrowseType)
        )
    )
)

app.add_handler(
    CallbackQueryHandler(
        browse.browse_books_navigator, filters=filters.create(
            lambda _, __, query: helpers.callback_matcher(query, BrowseNavigation)
        )
    )
)

app.add_handler(
    MessageHandler(
        search.search_books_message, filters=(
                filters.text & ~filters.via_bot &
                ~filters.create(lambda _, __, msg: msg.text.isdigit())
                & ~filters.create(lambda _, __, ms: len(ms.text) <= 2)
        )
    )
)

app.add_handler(
    CallbackQueryHandler(
        search.search_books_navigator, filters=filters.create(
            lambda _, __, query: helpers.callback_matcher(query, SearchNavigation)
        )
    )
)

app.add_handler(
    CallbackQueryHandler(
        utils.show_book, filters=filters.create(lambda _, __, query: helpers.callback_matcher(query, ShowBook))
    )
)

app.add_handler(
    CallbackQueryHandler(
        utils.read_book, filters=filters.create(lambda _, __, query: helpers.callback_matcher(query, ReadBook))
    )
)

app.add_handler(
    MessageHandler(
        utils.jump_to_page, filters=filters.create(
            lambda _, __, msg: msg.text.isdigit()
        ) & filters.create(jump_to_page_filter)
    )
)

app.add_handler(
    EditedMessageHandler(
        utils.jump_to_page, filters=filters.create(
            lambda _, __, msg: msg.text.isdigit()
        ) & filters.create(jump_to_page_filter)
    )
)

app.add_handler(
    CallbackQueryHandler(
        utils.jump_tip, filters=filters.create(
            lambda _, __, query: helpers.callback_matcher(query, JumpToPage)
        )
    )
)

if __name__ == '__main__':
    app.run()
