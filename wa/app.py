import wa.utils as utils
from fastapi import FastAPI
from pywa import WhatsApp
from pywa import filters as fil
from pywa.filters import TextFilter, CallbackFilter
from pywa.handlers import MessageHandler, ButtonCallbackHandler, SelectionCallbackHandler
from data.config import get_settings
from data.callbacks import ShowBook, ShareBook, SearchNavigation
from wa import search

conf = get_settings()

fastapi_app = FastAPI()

wa = WhatsApp(
    token=conf.wa_token,
    phone_id=conf.wa_phone_id,
    server=fastapi_app,
    verify_token=conf.wa_verify_token,
)

wa.add_handlers(
    MessageHandler(
        utils.on_start,
        TextFilter.command("start", "התחלה", prefixes=("!", "/")),
    ),
    MessageHandler(
        utils.show_help,
        fil.any_(
            TextFilter.command("help", "עזרה", prefixes=("!", "/")),
            TextFilter.match("?", "??"),
        ),
    ),
    MessageHandler(
        utils.show_commands,
        fil.any_(
            TextFilter.command("commands", "פקודות", prefixes=("!", "/")),
            TextFilter.match("!", "!!"),
        )
    ),
    ButtonCallbackHandler(
        utils.show_help,
        CallbackFilter.data_matches("help")
    ),
    ButtonCallbackHandler(
        utils.show_commands,
        CallbackFilter.data_matches("commands")
    ),
    SelectionCallbackHandler(
        utils.on_book,
        CallbackFilter.data_startswith(ShowBook.__clbname__)
    ),
    MessageHandler(
        utils.on_book,
        TextFilter.startswith(ShowBook.__clbname__)
    ),
    MessageHandler(
        search.on_search,
        TextFilter.ANY,
        TextFilter.length((3, 72)),
    ),
    SelectionCallbackHandler(
        search.on_search,
        CallbackFilter.data_startswith(SearchNavigation.__clbname__)
    ),
    ButtonCallbackHandler(
        utils.on_share,
        CallbackFilter.data_startswith(ShareBook.__clbname__)
    ),
)

