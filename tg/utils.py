from pyrogram import Client
from pyrogram.errors import MessageNotModified
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    CallbackQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineQuery,
)
from data.rate_limit import limiter, RateLimit
from db.repository import StatsType
from tg import helpers
from tg.helpers import Menu, get_string as gs, get_string_by_lang as gsbl
from data.callbacks import ShowBook, ReadBook, JumpToPage, BrowseType
from data.enums import BookType, ReadMode, Language
from data.strings import String as s  # noqa
from data import api
from db import repository


def start(_: Client, mc: Message | CallbackQuery):
    """Start message"""
    user_id = mc.from_user.id
    if isinstance(mc, Message) and not repository.is_tg_user_exists(tg_id=user_id):
        repository.add_tg_user(tg_id=user_id, lang=mc.from_user.language_code)
    kwargs = dict(
        text=gs(user_id, s.TG_WELCOME),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        gs(user_id, s.SEARCH), switch_inline_query_current_chat=""
                    ),
                    InlineKeyboardButton(
                        gs(user_id, s.BROWSE), callback_data=Menu.BROWSE
                    ),
                ],
                [
                    InlineKeyboardButton("📤", switch_inline_query=""),
                    InlineKeyboardButton(
                        text=gs(user_id, s.STATS), callback_data=Menu.STATS
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=gs(user_id, s.CHANGE_LANGUAGE),
                        callback_data=Menu.CHOOSE_LANG,
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=gs(user_id, s.HEBREWBOOKS_SITE),
                        url=Menu.HEBREWBOOKS_SITE_URL,
                    )
                ],
            ]
        ),
    )
    if isinstance(mc, Message):
        mc.reply_text(**kwargs)
    else:
        try:
            mc.edit_message_text(**kwargs)
        except MessageNotModified:
            pass


def choose_lang(_: Client, mc: Message | CallbackQuery):
    """
    Choose a language.
    """
    languages = [
        [
            InlineKeyboardButton(
                text=f"{lang.flag} {lang.name}", callback_data=f"lang:{lang.code}"
            )
        ]
        for lang in Language
    ]
    # meth = mc.reply_text if isinstance(mc, Message) else mc.edit_message_text
    mc.edit_message_text(
        text=gs(mc.from_user.id, s.CHOOSE_LANGUAGE),
        reply_markup=InlineKeyboardMarkup(
            [
                *languages,
                [
                    InlineKeyboardButton(
                        text=gs(mc.from_user.id, s.BACK), callback_data=Menu.START
                    )
                ],
            ]
        ),
    )


def set_lang(_: Client, clb: CallbackQuery):
    """
    Set a language.
    """
    _, lang_code = clb.data.split(":")
    repository.update_tg_user(
        tg_id=clb.from_user.id, lang=Language.from_code(lang_code).code
    )
    clb.answer(text=gs(clb.from_user.id, s.LANGUAGE_CHANGED), show_alert=True)
    start(_, clb)


def show_stats(_: Client, clb: CallbackQuery):
    """
    Show stats.
    """
    user_id = clb.from_user.id
    stats = repository.get_stats()
    if helpers.is_admin(user_id):
        clb.answer(
            text=gs(
                user_id,
                s.SHOW_STATS_ADMIN,
                tg_users_count=repository.get_tg_users_count(),
                wa_users_count=repository.get_wa_users_count(),
                books_read=stats.books_read,
                pages_read=stats.pages_read,
                inline_searches=stats.inline_searches,
                msg_searches=stats.msg_searches,
                jumps=stats.jumps,
            ),
            show_alert=True,
        )
    else:
        clb.answer(
            text=gs(
                user_id,
                s.SHOW_STATS,
                books_read=stats.books_read,
                pages_read=stats.pages_read,
                searches=stats.searches,
            ),
            show_alert=True,
            cache_time=100,
        )


def show_book(_: Client, clb: CallbackQuery):
    """
    Show a book.
    """
    user_id = clb.from_user.id
    if (
        seconds := limiter.get_seconds_to_wait(
            user_id=user_id, rate_limit_type=RateLimit.PDF_FULL
        )
    ) > 0:
        clb.answer(
            text=gs(
                user_id,
                s.WAIT_X_MINUTES if seconds >= 60 else s.WAIT_X_SECONDS,
                x=int(seconds // 60 if seconds >= 60 else seconds),
            ),
            show_alert=True,
        )
        return
    _book_id, *others = clb.data.split(",")
    book = api.get_book(ShowBook.from_callback(_book_id).id)
    clb.edit_message_text(
        text=helpers.get_book_text(book),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=gs(user_id=user_id, string=s.INSTANT_READ),
                        callback_data=ReadBook(
                            id=str(book.id),
                            page=1,
                            total=book.pages,
                            read_mode=ReadMode.IMAGE,
                            book_type=BookType.BOOK,
                        ).join_to_callback(ShowBook(id=book.id), *others),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=gs(user_id=user_id, string=s.SHARE),
                        switch_inline_query=str(book.id),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=gs(user_id=user_id, string=s.DOWNLOAD), url=book.pdf_url
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=gs(user_id=user_id, string=s.BACK),
                        callback_data=",".join(others),
                    )
                ]
                if others
                else others,
            ],
        ),
    )
    repository.increase_stats(StatsType.BOOKS_READ)


def read_book(_: Client, clb: CallbackQuery):
    """
    Read a book.
    """
    user_id = clb.from_user.id
    if not repository.is_tg_user_exists(tg_id=user_id):
        on_unregistered_user(user_lang=clb.from_user.language_code, query=clb)
        return
    book, masechet, tursa, previous_tursa, total = None, None, None, None, None
    _read_book, *others = clb.data.split(",")
    read_clb = ReadBook.from_callback(_read_book)
    if (
        seconds := limiter.get_seconds_to_wait(
            user_id=user_id,
            rate_limit_type=RateLimit.IMAGE_PAGE
            if read_clb.read_mode == ReadMode.IMAGE
            else RateLimit.PDF_PAGE,
        )
    ) > 0:
        clb.answer(
            text=gs(
                user_id,
                (s.WAIT_X_MINUTES if seconds >= 60 else s.WAIT_X_SECONDS),
                x=int(seconds // 60 if seconds >= 60 else seconds),
            ),
            show_alert=True,
        )
        return

    if read_clb.book_type == BookType.BOOK:
        book = api.get_book(int(read_clb.id))
        total = book.pages
    elif read_clb.book_type == BookType.MASECHET:
        masechet = api.get_masechet(int(read_clb.id))
        total = masechet.total
    elif read_clb.book_type == BookType.TURSA:
        _previous_tursa = BrowseType.from_callback(others[0])
        _previous_previous_tursa = BrowseType.from_callback(others[1])
        tursa = next(
            filter(lambda x: x.id == read_clb.id, api.get_tursa(_previous_tursa.id))
        )
        previous_tursa = next(
            filter(
                lambda x: x.id == _previous_tursa.id,
                api.get_tursa(_previous_previous_tursa.id),
            )
        )
    else:
        raise ValueError("Invalid book type")
    clb.answer(text=gs(user_id=user_id, string=s.WAIT_FOR_PREVIEW), show_alert=False)
    try:
        clb.edit_message_text(
            text="".join(
                (
                    gs(user_id=user_id, string=s.INSTANT_READ),
                    "\n\n",
                    helpers.get_book_text(
                        book=book, page=read_clb.page, read_mode=read_clb.read_mode
                    )
                    if read_clb.book_type == BookType.BOOK
                    else helpers.get_masechet_page_text(
                        masechet=masechet,
                        page=read_clb.page,
                        read_mode=read_clb.read_mode,
                    )
                    if read_clb.book_type == BookType.MASECHET
                    else helpers.get_tursa_text(
                        tursa=tursa, previous_tursa=previous_tursa
                    ),
                )
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    helpers.read_mode_chooser(
                        user_id=user_id,
                        read_clb=read_clb,
                        page=read_clb.page,
                        others=others,
                        read_modes=(ReadMode.PDF, ReadMode.IMAGE)
                        if read_clb.book_type != BookType.TURSA
                        else (),
                    ),
                    helpers.next_previous_buttons(
                        user_id=user_id,
                        read_clb=read_clb,
                        page=read_clb.page,
                        total=total,
                        others=others,
                    ),
                    [
                        InlineKeyboardButton(
                            text=gs(user_id=user_id, string=s.READ_ON_SITE),
                            url=book.get_page_url(read_clb.page)
                            if read_clb.book_type == BookType.BOOK
                            else masechet.pages[read_clb.page - 1].get_page_url()
                            if read_clb.book_type == BookType.MASECHET
                            else tursa.url,
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text=gs(user_id=user_id, string=s.BACK),
                            callback_data=",".join(others),
                        )
                    ],
                ]
            ),
        )
        repository.increase_stats(StatsType.PAGES_READ)
    except MessageNotModified:
        clb.answer(text=gs(user_id=user_id, string=s.SLOW_DOWN))


def jump_to_page(_: Client, msg: Message):
    """
    Jump to a page.

    msg.text: number
    """
    masechet, book = None, None
    user_id = msg.from_user.id
    try:
        jump_button = next(
            filter(
                lambda b: helpers.callback_matcher(b.callback_data, JumpToPage),
                msg.reply_to_message.reply_markup.inline_keyboard[1],
            )
        )
    except (StopIteration, IndexError):
        return
    jump_clb = JumpToPage.from_callback(jump_button.callback_data)
    _next_or_previous = next(
        filter(
            lambda b: helpers.callback_matcher(b.callback_data, ReadBook),
            msg.reply_to_message.reply_markup.inline_keyboard[1:-1][0],
        )
    )
    next_or_previous, *nop_others = _next_or_previous.callback_data.split(",")
    nop_clb = ReadBook.from_callback(next_or_previous)
    is_book = jump_clb.book_type == BookType.BOOK
    if (
        seconds := limiter.get_seconds_to_wait(
            user_id=user_id,
            rate_limit_type=RateLimit.IMAGE_PAGE
            if nop_clb.read_mode == ReadMode.IMAGE
            else RateLimit.PDF_PAGE,
        )
    ) > 0:
        msg.reply(
            text=gs(
                user_id,
                s.WAIT_X_MINUTES if seconds >= 60 else s.WAIT_X_SECONDS,
                x=int(seconds // 60 if seconds >= 60 else seconds),
            ),
            quote=True,
        )
        return
    if not is_book:
        masechet = api.get_masechet(jump_clb.id)
        try:
            jump_to = (
                masechet.pages.index(
                    next(filter(lambda p: p.name == msg.text, masechet.pages))
                )
                + 1
            )
        except (StopIteration, ValueError):
            msg.reply_text(
                text=gs(
                    user_id=user_id,
                    string=s.PAGE_NOT_EXIST_CHOOSE_BETWEEN_X_Y,
                    x=masechet.pages[0].name,
                    y=masechet.pages[-1].name,
                )
            )
            return
    else:
        try:
            jump_to = int(msg.text)
            if jump_to > jump_clb.total or jump_to < 1:
                msg.reply_text(
                    text=gs(
                        user_id=user_id,
                        string=s.PAGE_NOT_EXIST_CHOOSE_BETWEEN_X_Y,
                        x=1,
                        y=jump_clb.total,
                    )
                )
                return
        except ValueError:
            msg.reply_text(text=gs(user_id=user_id, string=s.NUMBERS_ONLY))
            return
        book = api.get_book(jump_clb.id)

    kwargs = dict(
        text="".join(
            (
                gs(user_id=user_id, string=s.INSTANT_READ),
                "\n\n",
                helpers.get_book_text(
                    book=book, page=jump_to, read_mode=nop_clb.read_mode
                )
                if is_book
                else helpers.get_masechet_page_text(
                    masechet=masechet, page=jump_to, read_mode=nop_clb.read_mode
                ),
            )
        ),
        reply_markup=InlineKeyboardMarkup(
            [
                helpers.read_mode_chooser(
                    user_id=user_id, read_clb=nop_clb, page=jump_to, others=nop_others
                ),
                helpers.next_previous_buttons(
                    user_id=user_id,
                    read_clb=nop_clb,
                    page=jump_to,
                    total=jump_clb.total,
                    others=nop_others,
                ),
                [
                    InlineKeyboardButton(
                        text=gs(user_id=user_id, string=s.READ_ON_SITE),
                        url=book.get_page_url(jump_clb.page)
                        if is_book
                        else masechet.pages[jump_clb.page - 1].get_page_url(),
                    )
                ],
                [msg.reply_to_message.reply_markup.inline_keyboard[-1][-1]],
            ]
        ),
    )
    if msg.reply_to_message.via_bot:
        msg.reply(**kwargs)  # Can't edit messages sent by the user
    else:
        msg.reply_to_message.edit(**kwargs)
    repository.increase_stats(StatsType.PAGES_READ)
    repository.increase_stats(StatsType.JUMPS)


def jump_tip(_: Client, clb: CallbackQuery):
    """
    Jump to a page tip.
    """
    user_id = clb.from_user.id
    if not repository.is_tg_user_exists(tg_id=user_id):
        on_unregistered_user(user_lang=clb.from_user.language_code, query=clb)
        return
    clb.answer(
        text=gs(user_id=user_id, string=s.JUMP_ALSO_BY_EDIT_TIP), show_alert=True
    )


def on_unregistered_user(user_lang: str, query: CallbackQuery | InlineQuery):
    query.answer(
        results=[
            InlineQueryResultArticle(
                title=gsbl(lang=user_lang, string=s.NOT_REGISTERED_TITLE),
                description=gsbl(lang=user_lang, string=s.NOT_REGISTERED_BODY),
                thumb_url="https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/"
                "Forbidden_Symbol_Transparent.svg/2048px-Forbidden_Symbol_Transparent.svg.png",
                input_message_content=InputTextMessageContent("/start"),
            )
        ],
        switch_pm_text=gsbl(lang=user_lang, string=s.CLICK_TO_REGISTER),
        switch_pm_parameter="start",
    ) if isinstance(query, InlineQuery) else query.answer(
        text=f"{gsbl(lang=user_lang, string=s.NOT_REGISTERED_TITLE)}\n\n"
        f"{gsbl(lang=user_lang, string=s.NOT_REGISTERED_BODY)}",
        show_alert=True,
    )
