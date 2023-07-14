import logging
import wa.utils as utils
from wa.helpers import Commands, DEFAULT_LANGUAGE
from wa.utils import Menu
from wa import search, browse
from fastapi import FastAPI
from pywa import WhatsApp
from pywa.filters import TextFilter, CallbackFilter
from pywa.handlers import MessageHandler, ButtonCallbackHandler, SelectionCallbackHandler
from data.config import get_settings
from data.callbacks import ShowBook, ShareBook, SearchNavigation, BrowseType, ReadBook
from db import repository

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
file_handler = logging.handlers.RotatingFileHandler(filename='wa.log', maxBytes=5 * 1024 * 1024, backupCount=1,
                                                    mode='D')
file_handler.setLevel(logging.DEBUG)
logging.basicConfig(
    level=conf.log_level,
    format="Time: %(asctime)s | Level: %(levelname)s | Module: %(module)s | Message: %(message)s",
    handlers=[console_handler, file_handler],
)

wa.add_handlers(
    MessageHandler(
        search.on_search,
        TextFilter.ANY,
        TextFilter.length((3, 72)),
    ),
    SelectionCallbackHandler(
        utils.show_book,
        CallbackFilter.data_startswith(ShowBook.__clbname__)
    ),
    SelectionCallbackHandler(
        search.on_search,
        CallbackFilter.data_startswith(SearchNavigation.__clbname__)
    ),
    MessageHandler(
        utils.show_book,
        TextFilter.startswith(ShowBook.__clbname__),
        lambda _, m: len(m.text.split(':')) == 2
    ),
    ButtonCallbackHandler(
        utils.read_book,
        CallbackFilter.data_startswith(ReadBook.__clbname__)
    ),
    MessageHandler(
        utils.read_book,
        TextFilter.startswith(ShowBook.__clbname__),
        lambda _, m: len(m.text.split(':')) == 3
    ),
    MessageHandler(
        utils.on_start,
        TextFilter.command("start", "התחל", "התחלה", prefixes=("!", "/")),
    ),
    ButtonCallbackHandler(
        utils.on_start,
        CallbackFilter.data_match("start"),
    ),
    ButtonCallbackHandler(
        utils.on_share_btn,
        CallbackFilter.data_startswith(ShareBook.__clbname__)
    ),
    ButtonCallbackHandler(
        utils.on_search_btn,
        CallbackFilter.data_match(Menu.SEARCH)
    ),
    ButtonCallbackHandler(
        utils.on_stats_btn,
        CallbackFilter.data_match(Menu.STATS)
    ),
    ButtonCallbackHandler(
        utils.on_about_btn,
        CallbackFilter.data_match(Menu.ABOUT)
    ),

)

wa.add_handlers(MessageHandler(lambda _, msg: repository.add_wa_user(msg.from_user.wa_id, DEFAULT_LANGUAGE)))
