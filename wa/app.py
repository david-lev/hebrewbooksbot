import logging
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
console_handler = logging.StreamHandler()
console_handler.setLevel(conf.log_level)
file_handler = logging.handlers.RotatingFileHandler(filename='wa.log', maxBytes=5 * 1024 * 1024, backupCount=1, mode='D')
file_handler.setLevel(logging.DEBUG)
logging.basicConfig(
    level=logging.INFO,
    format="Time: %(asctime)s | Level: %(levelname)s | Module: %(module)s | Message: %(message)s",
    handlers=[console_handler, file_handler],
)

wa.add_handlers(
    MessageHandler(
        utils.on_start,
        TextFilter.command("start", "התחל", "התחלה", prefixes=("!", "/")),
    ),
    # MessageHandler(
    #     utils.show_help,
    #     fil.any_(
    #         TextFilter.command("help", "עזרה", prefixes=("!", "/")),
    #         TextFilter.match("?", "??"),
    #     ),
    # ),
    # MessageHandler(
    #     utils.show_commands,
    #     fil.any_(
    #         TextFilter.command("commands", "פקודות", prefixes=("!", "/")),
    #         TextFilter.match("!", "!!"),
    #     )
    # ),
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

