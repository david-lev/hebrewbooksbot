from pyrogram import Client, filters
from pyrogram.handlers import (
    InlineQueryHandler,
    MessageHandler,
    CallbackQueryHandler,
    EditedMessageHandler,
)
from pyrogram.types import BotCommand
from data import config, strings
from data.enums import Language
from tg import search, helpers
from tg import browse
from tg import utils
from tg.helpers import jump_to_page_filter, Menu
from data.callbacks import (
    BrowseNavigation,
    BrowseType,
    ShowBook,
    SearchNavigation,
    ReadBook,
    JumpToPage,
)
from tg.helpers import get_string as gs
from data.strings import String as s

cfg = config.get_settings()

app = Client(
    name="hebrewbooksbot",
    # workdir="../",
    api_id=cfg.tg_api_id,
    api_hash=cfg.tg_api_hash,
    bot_token=cfg.tg_bot_token,
)

app.add_handler(MessageHandler(utils.start, filters=filters.command(Menu.START)))

if cfg.under_maintenance:
    app.add_handler(
        MessageHandler(
            callback=lambda _, m: m.reply_text(
                gs(m.from_user.id, s.BOT_UNDER_MAINTENANCE)
            ),
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            lambda _, cq: cq.answer(
                text=gs(cq, s.BOT_UNDER_MAINTENANCE), show_alert=True
            ),
        )
    )
    app.add_handler(
        InlineQueryHandler(
            lambda _, iq: iq.answer(
                results=[],
                switch_pm_text=gs(iq, s.BOT_UNDER_MAINTENANCE),
                switch_pm_parameter="start",
            ),
        )
    )
else:
    app.add_handler(
        CallbackQueryHandler(
            utils.choose_lang,
            filters=filters.create(
                lambda _, __, query: query.data.startswith(Menu.CHOOSE_LANG)
            ),
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            utils.set_lang,
            filters=filters.create(lambda _, __, query: query.data.startswith("lang:")),
        )
    )
    app.add_handler(
        CallbackQueryHandler(
            utils.start,
            filters=filters.create(lambda _, __, query: query.data == Menu.START),
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            utils.show_stats,
            filters=filters.create(lambda _, __, query: query.data == Menu.STATS),
        )
    )

    app.add_handler(
        InlineQueryHandler(
            search.search_books_inline,
            filters=filters.create(lambda _, __, query: len(query.query) > 2),
        ),
    )

    app.add_handler(
        InlineQueryHandler(
            search.empty_search,
            filters=filters.create(lambda _, __, query: len(query.query) <= 2),
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            browse.browse_menu,
            filters=filters.create(lambda _, __, query: query.data == Menu.BROWSE),
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            browse.browse_types,
            filters=filters.create(
                lambda _, __, query: helpers.callback_matcher(query, BrowseType)
            ),
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            browse.browse_books_navigator,
            filters=filters.create(
                lambda _, __, query: helpers.callback_matcher(query, BrowseNavigation)
            ),
        )
    )

    app.add_handler(
        MessageHandler(
            search.search_books_message, filters=helpers.MESSAGE_SEARCH_FILTER
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            search.search_books_navigator,
            filters=filters.create(
                lambda _, __, query: helpers.callback_matcher(query, SearchNavigation)
            ),
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            utils.show_book,
            filters=filters.create(
                lambda _, __, query: helpers.callback_matcher(query, ShowBook)
            ),
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            utils.read_book,
            filters=filters.create(
                lambda _, __, query: helpers.callback_matcher(query, ReadBook)
            ),
        )
    )

    app.add_handler(
        MessageHandler(
            utils.jump_to_page,
            filters=filters.reply & filters.create(jump_to_page_filter),
        )
    )

    app.add_handler(
        EditedMessageHandler(
            utils.jump_to_page, filters=filters.create(jump_to_page_filter)
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            utils.jump_tip,
            filters=filters.create(
                lambda _, __, query: helpers.callback_matcher(query, JumpToPage)
            ),
        )
    )

if __name__ == "__main__":
    # app.start()
    # for lang in Language:
    #     app.set_bot_commands(
    #         commands=[
    #             BotCommand(command="start", description=strings.get_string(s.START_CMD_DESC, lang)),
    #             BotCommand(command="browse", description=strings.get_string(s.BROWSE_CMD_DESC, lang)),
    #             BotCommand(command="search", description=strings.get_string(s.SEARCH_CMD_DESC, lang)),
    #             BotCommand(command="stats", description=strings.get_string(s.STATS_CMD_DESC, lang)),
    #             BotCommand(command="contact", description=strings.get_string(s.CONTACT_US_CMD_DESC, lang)),
    #             BotCommand(command="lang", description=strings.get_string(s.CHANGE_LANG_CMD_DESC, lang)),
    #         ],
    #         language_code=lang.code
    #     )
    # app.stop()
    app.run()
