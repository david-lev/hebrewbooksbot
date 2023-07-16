import logging
import wa.utils as utils
from fastapi import FastAPI
from pywa import WhatsApp, filters as fil
from pywa.filters import TextFilter, CallbackFilter
from pywa.handlers import MessageHandler, ButtonCallbackHandler, SelectionCallbackHandler
from pywa.types import Message
from data.callbacks import ShowBook, ShareBook, SearchNavigation, ReadBook
from data.config import get_settings
from db import repository
from wa import search
from wa.helpers import DEFAULT_LANGUAGE
from wa.utils import Menu

conf = get_settings()
fastapi_app = FastAPI()
wa = WhatsApp(
    token=conf.wa_token,
    phone_id=conf.wa_phone_id,
    server=fastapi_app,
    verify_token=conf.wa_verify_token,
    webhook_endpoint='/wa_webhook',
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

start_filter = TextFilter.command("start", "התחל", "התחלה", prefixes=("!", "/"))

wa.add_handlers(
    MessageHandler(
        search.on_search,
        TextFilter.ANY,
        TextFilter.length((3, 72)),
        fil.not_(fil.REPLY),
        lambda _, m: not m.text.isdigit()
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
        utils.jump_to_page, fil.REPLY
    ),
    MessageHandler(
        utils.on_start, start_filter,
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


@wa.on_message()
def on_new_user(client: WhatsApp, msg: Message):
    if repository.add_wa_user(msg.from_user.wa_id, DEFAULT_LANGUAGE) and fil.not_(start_filter)(client, msg):
        utils.on_start(client, msg)
