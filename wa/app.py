import logging
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pywa import WhatsApp, filters as fil
from pywa.handlers import MessageHandler, CallbackButtonHandler, CallbackSelectionHandler, MessageStatusHandler
from pywa.types import Message
from data.callbacks import ShowBook, ShareBook, SearchNavigation, ReadBook
from data.config import get_settings
from db import repository
from data.strings import String as s  # noqa
from wa import search, helpers, utils

conf = get_settings()
fastapi_app = FastAPI()


@fastapi_app.exception_handler(RequestValidationError)
async def request_validation_error_handler(_: Request, exc: RequestValidationError):
    logging.error(f"Invalid request. detail: {exc.errors()}, body: {exc.body}")

wa = WhatsApp(
    token=conf.wa_token,
    phone_id=conf.wa_phone_id,
    server=fastapi_app,
    verify_token=conf.wa_verify_token,
    webhook_endpoint='/wa_webhook',
)

active_filter = lambda _, m: repository.is_wa_user_active(wa_id=m.from_user.wa_id)  # noqa
admins_filter = lambda _, m: m.from_user.wa_id in conf.wa_admins  # noqa

wa.add_handlers(MessageStatusHandler(utils.on_failed_message, fil.message_status.failed))

if conf.under_maintenance:
    @wa.on_message()
    def register_user(_: WhatsApp, msg: Message):
        wa_id = msg.from_user.wa_id
        if not repository.is_wa_user_exists(wa_id=wa_id):
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
        wa_id = msg.from_user.wa_id
        if (not repository.is_wa_user_exists(wa_id=wa_id) and
                repository.add_wa_user(
                wa_id=msg.from_user.wa_id,
                lang=helpers.phone_number_to_lang(msg.from_user.wa_id).code,
                active=(allowed := fil.from_countries(helpers.SUPPORTED_COUNTRIES)(client, msg))
        )):
            if allowed:
                utils.on_start(client, msg)
            else:
                logging.info(f"User {msg.from_user.wa_id} is not allowed to use the bot.")


    wa.add_handlers(
        MessageHandler(
            search.on_search,
            active_filter,
            fil.not_(fil.text.is_command),
            fil.text.length((1, 72)),  # description limit
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
            active_filter,
            fil.text.startswith(ShowBook.__clbname__),
            lambda _, m: m.text is not None and len(m.text.split(':')) == 2
        ),
        CallbackButtonHandler(
            utils.read_book,
            fil.callback.data_startswith(ReadBook.__clbname__)
        ),
        MessageHandler(
            utils.read_book,
            active_filter,
            fil.text.startswith(ShowBook.__clbname__), lambda _, m: m.text is not None and len(m.text.split(':')) == 3
        ),
        MessageHandler(
            utils.jump_to_page,
            active_filter, fil.reply
        ),
        MessageHandler(
            utils.on_start,
            active_filter,
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
            utils.on_about_btn,
            fil.callback.data_matches(utils.Menu.ABOUT)
        ),
        CallbackButtonHandler(
            utils.on_acknowledgements_btn,
            fil.callback.data_matches(utils.Menu.ACKNOWLEDGEMENTS)
        ),
        MessageHandler(
            utils.unblock_user_admin,
            admins_filter, fil.text.command("unblock", "un", prefixes=("!", "/")),
        ),
        MessageHandler(
            utils.on_stats_admin,
            admins_filter, fil.text.command("stats", prefixes=("!", "/")),
        ),
    )
