import logging
from fastapi import FastAPI
from pywa import WhatsApp, filters as fil
from pywa.handlers import MessageHandler, CallbackButtonHandler, CallbackSelectionHandler
from pywa.types import Message, MessageStatus
from data.callbacks import ShowBook, ShareBook, SearchNavigation, ReadBook
from data.config import get_settings
from db import repository
from data.strings import String as s  # noqa
from wa import search, helpers, utils

conf = get_settings()
fastapi_app = FastAPI()
wa = WhatsApp(
    token=conf.wa_token,
    phone_id=conf.wa_phone_id,
    server=fastapi_app,
    verify_token=conf.wa_verify_token,
    webhook_endpoint='/wa_webhook',
)
# console_handler = logging.StreamHandler()
# console_handler.setLevel(conf.log_level)
# file_handler = logging.handlers.RotatingFileHandler(filename='wa.log', maxBytes=5 * (2 ** 20), backupCount=1, mode='D')
# file_handler.setLevel(logging.DEBUG)
# logging.basicConfig(
#     level=conf.log_level,
#     format="Time: %(asctime)s | Level: %(levelname)s | Module: %(module)s | Message: %(message)s",
#     handlers=[console_handler, file_handler],
# )

country_filter = lambda _, m: m.from_user.wa_id.startswith(helpers.SUPPORTED_COUNTRIES)  # noqa

if conf.under_maintenance:
    @wa.on_message()
    def register_user(_: WhatsApp, msg: Message):
        wa_id = msg.from_user.wa_id
        repository.add_wa_user(
            wa_id=wa_id,
            lang=helpers.phone_number_to_lang(wa_id).code,
            active=False
        )
        if conf.reply_under_maintenance:
            msg.reply_text(text=helpers.get_string(wa_id, s.BOT_UNDER_MAINTENANCE))

else:

    @wa.on_message()
    def on_new_user(client: WhatsApp, msg: Message):
        if repository.add_wa_user(
                wa_id=msg.from_user.wa_id,
                lang=helpers.phone_number_to_lang(msg.from_user.wa_id).code,
                active=(allowed := country_filter(client, msg))
        ):
            if allowed:
                utils.on_start(client, msg)
            else:
                logging.info(f"User {msg.from_user.wa_id} is not allowed to use the bot.")


    wa.add_handlers(
        MessageHandler(
            search.on_search,
            country_filter,
            fil.text,
            fil.text.length((3, 72)),
            fil.not_(fil.reply),
            lambda _, m: m.text is not None and not m.text.isdigit()
        ),
        CallbackSelectionHandler(
            utils.show_book,
            fil.callback.data_startswith(ShowBook.__clbname__)
        ),
        CallbackSelectionHandler(
            search.on_search,
            fil.callback.data_startswith(SearchNavigation.__clbname__)
        ),
        MessageHandler(
            utils.show_book,
            country_filter,
            fil.text.startswith(ShowBook.__clbname__),
            lambda _, m: m.text is not None and len(m.text.split(':')) == 2
        ),
        CallbackButtonHandler(
            utils.read_book,
            fil.callback.data_startswith(ReadBook.__clbname__)
        ),
        MessageHandler(
            utils.read_book,
            country_filter,
            fil.text.startswith(ShowBook.__clbname__), lambda _, m: m.text is not None and len(m.text.split(':')) == 3
        ),
        MessageHandler(
            utils.jump_to_page,
            country_filter, fil.reply
        ),
        MessageHandler(
            utils.on_start,
            country_filter,
            fil.text.command("start", "התחל", "התחלה", prefixes=("!", "/")),
        ),
        CallbackButtonHandler(
            utils.on_start,
            fil.callback.data_matches(utils.Menu.START),
        ),
        CallbackButtonHandler(
            utils.on_change_language,
            fil.callback.data_matches(utils.Menu.CHANGE_LANGUAGE),
        ),
        CallbackSelectionHandler(
            utils.on_language_selected,
            fil.callback.data_startswith("lang:"),
        ),
        CallbackButtonHandler(
            utils.on_share_btn,
            fil.callback.data_startswith(ShareBook.__clbname__)
        ),
        CallbackButtonHandler(
            utils.on_search_btn,
            fil.callback.data_matches(utils.Menu.SEARCH)
        ),
        CallbackButtonHandler(
            utils.on_stats_btn,
            fil.callback.data_matches(utils.Menu.STATS)
        ),
        CallbackButtonHandler(
            utils.on_about_btn,
            fil.callback.data_matches(utils.Menu.ABOUT)
        ),

    )


@wa.on_message_status(fil.message_status.failed)
def on_message_failed(_: WhatsApp, status: MessageStatus):
    logging.error(f"Message failed to send to {status.from_user.wa_id} with error: {status.error}")
